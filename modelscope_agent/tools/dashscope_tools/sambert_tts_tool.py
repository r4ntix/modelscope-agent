import os

from modelscope_agent.tools.base import BaseTool, register_tool
from pydantic import ValidationError

WORK_DIR = os.getenv('CODE_INTERPRETER_WORK_DIR', '/tmp/ci_workspace')


@register_tool('sambert_tts')
class SambertTtsTool(BaseTool):
    description = 'Sambert语音合成服务，将文本转成语音'
    name = 'sambert_tts'
    parameters: list = [{
        'name': 'text',
        'description': '需要转成语音的文本',
        'required': True,
        'type': 'string'
    }]

    def __init__(self, cfg={}):
        self.cfg = cfg.get(self.name, {})

        self.api_key = self.cfg.get('dashscope_api_key',
                                    os.environ.get('DASHSCOPE_API_KEY'))
        if self.api_key is None:
            raise ValueError('Please set valid DASHSCOPE_API_KEY!')

        super().__init__(cfg)

    def call(self, params: str, **kwargs) -> str:
        from dashscope.audio.tts import SpeechSynthesizer
        params = self._verify_args(params)
        tts_text = params['text']
        if tts_text is None or len(tts_text) == 0 or tts_text == '':
            raise ValueError('tts input text is valid')
        os.makedirs(WORK_DIR, exist_ok=True)
        wav_file = WORK_DIR + '/sambert_tts_audio.wav'
        response = SpeechSynthesizer.call(
            model='sambert-zhijia-v1', format='wav', text=tts_text)
        if response.get_audio_data() is not None:
            with open(wav_file, 'wb') as f:
                f.write(response.get_audio_data())
        else:
            raise ValueError(
                f'call sambert tts failed, request id: {response.get_response().request_id}'
            )
        return wav_file
