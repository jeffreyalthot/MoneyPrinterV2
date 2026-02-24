import os
import sys
import site

from config import ROOT_DIR, get_offline_mode
from local_ai import synthesize_beep_speech


class TTS:
    """Class for Text-to-Speech using Coqui TTS with local fallback."""

    def __init__(self) -> None:
        self._synthesizer = None

        if get_offline_mode():
            return

        try:
            from TTS.utils.manage import ModelManager
            from TTS.utils.synthesizer import Synthesizer
        except Exception:
            # Pydroid/low-resource fallback
            return

        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            site_packages = site.getsitepackages()[0]
        else:
            site_packages = site.getusersitepackages()

        models_json_path = os.path.join(site_packages, "TTS", ".models.json")
        tts_dir = os.path.dirname(models_json_path)
        if not os.path.exists(tts_dir):
            os.makedirs(tts_dir)

        model_manager = ModelManager(models_json_path)
        model_path, config_path, _ = model_manager.download_model("tts_models/en/ljspeech/tacotron2-DDC_ph")
        voc_path, voc_config_path, _ = model_manager.download_model("vocoder_models/en/ljspeech/univnet")

        self._synthesizer = Synthesizer(
            tts_checkpoint=model_path,
            tts_config_path=config_path,
            vocoder_checkpoint=voc_path,
            vocoder_config=voc_config_path,
        )

    @property
    def synthesizer(self):
        return self._synthesizer

    def synthesize(self, text: str, output_file: str = os.path.join(ROOT_DIR, ".mp", "audio.wav")) -> str:
        if self.synthesizer is None:
            return synthesize_beep_speech(text, output_file)

        outputs = self.synthesizer.tts(text)
        self.synthesizer.save_wav(outputs, output_file)
        return output_file
