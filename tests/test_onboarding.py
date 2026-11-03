"""Guided paths must not read a backup, export a key or launch a browser implicitly."""
import sys
from pathlib import Path
import tkinter as tk
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import did_talisman as app
from onboarding import COPY, ROUTES, PARAGRAPHS, SIGNER_GUIDE_URL, SIGNER_GUIDE_URL_FR

class OnboardingTests(unittest.TestCase):
    def setUp(self):
        self.root=tk.Tk()
        self.root.withdraw()
        self.view=app.ImportWindow(self.root,"fr")
        self.guide=self.view.onboarding
        self.root.update_idletasks()

    def tearDown(self):
        self.root.update_idletasks()
        self.root.destroy()

    def test_start_hides_form_and_has_no_identity_defaults(self):
        self.assertEqual("start",self.guide.step)
        self.assertFalse(self.guide.form_visible)
        self.assertEqual({},self.view.identity_card.grid_info())
        self.assertEqual({},self.view.details.grid_info())
        self.assertTrue(all(value.get()=="" for value in self.view.fields.values()))
        self.assertEqual(set(COPY["fr"]),set(COPY["en"]))

    def test_navigation_never_converts_or_reads_selected_backup(self):
        self.view.fields["source"].set("nonexistent-private-backup.pem")
        with patch.object(app,"export_existing",side_effect=AssertionError("No export in guide")) as export:
            for lang in ("en","fr"):
                self.view.switch_language(lang)
                for step in list(ROUTES)+list(PARAGRAPHS):
                    self.assertTrue(self.guide.show(step))
                    self.root.update_idletasks()
                    self.assertFalse(self.guide.form_visible)
                    self.assertEqual({},self.view.identity_card.grid_info())
            export.assert_not_called()

    def test_pem_path_requires_acknowledgement_and_keeps_export_consent_separate(self):
        self.guide.show("pem")
        self.assertFalse(self.guide.open_form())
        self.assertTrue(self.guide.continue_button.instate(["disabled"]))
        self.guide.toggle_ready()
        self.assertTrue(self.guide.open_form())
        self.assertTrue(self.guide.form_visible)
        self.assertFalse(self.view.consent.get())
        with patch.object(app,"export_existing") as export:
            self.view.start_export()
            export.assert_not_called()
        self.assertFalse(self.view.busy)

    def test_language_changes_keep_path_acknowledgement_and_form_values(self):
        self.guide.show("pem")
        self.guide.toggle_ready()
        self.view.fields["old"].set("public-demo-password")
        for lang in ("en","fr"):
            self.view.switch_language(lang)
            self.assertEqual("pem",self.guide.step)
            self.assertTrue(self.guide.ready.get())
            self.assertEqual(COPY[lang]["open_form"],self.guide.continue_button.cget("text"))
            self.assertEqual("public-demo-password",self.view.fields["old"].get())
        self.guide.open_form()
        self.view.switch_language("en")
        self.assertTrue(self.guide.form_visible)
        self.assertEqual("public-demo-password",self.view.fields["old"].get())
        self.guide.show("start")
        self.assertFalse(self.guide.ready.get())

    def test_wallet_json_and_missing_paths_do_not_enter_the_pem_form(self):
        with patch.object(app,"export_existing") as export:
            for step in ("wallet","json","missing","locate","other","signer"):
                self.guide.show(step)
                self.guide.ready.set(True)
                self.assertFalse(self.guide.open_form())
                self.view.consent.set(True)
                self.view.start_export()
                self.assertFalse(self.view.busy)
            export.assert_not_called()

    def test_signer_link_opens_only_after_explicit_action(self):
        def descendants(widget):
            for child in widget.winfo_children():
                yield child
                yield from descendants(child)
        with patch("onboarding.webbrowser.open") as opened:
            self.guide.show("signer")
            self.view.switch_language("en")
            opened.assert_not_called()
            buttons=[w for w in descendants(self.guide.container)
                     if isinstance(w,self.view.ttk.Button)
                     and w.cget("text")==COPY["en"]["signer_docs"]]
            self.assertEqual(1,len(buttons))
            buttons[0].invoke()
            opened.assert_called_once_with(SIGNER_GUIDE_URL)
            self.view.switch_language("fr")
            buttons=[w for w in descendants(self.guide.container)
                     if isinstance(w,self.view.ttk.Button)
                     and w.cget("text")==COPY["fr"]["signer_docs"]]
            self.assertEqual(1,len(buttons))
            buttons[0].invoke()
            self.assertEqual(SIGNER_GUIDE_URL_FR,opened.call_args.args[0])

if __name__=="__main__":
    unittest.main()
