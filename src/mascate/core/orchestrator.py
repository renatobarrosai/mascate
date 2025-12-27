"""Orquestrador Principal do Mascate.

Conecta áudio, inteligência, execução e interface em um loop de eventos.
"""

from __future__ import annotations

import json
import logging
import time
from enum import Enum
from typing import Any

from mascate.audio.pipeline import AudioPipeline
from mascate.audio.tts.piper import PiperTTS
from mascate.executor.executor import Executor
from mascate.intelligence.brain import Brain
from mascate.interface.hud import HUD

logger = logging.getLogger(__name__)


class SystemState(Enum):
    """Estados globais do assistente."""

    INITIALIZING = "INITIALIZING"
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    PROCESSING = "PROCESSING"
    EXECUTING = "EXECUTING"
    SPEAKING = "SPEAKING"
    CONFIRMING = "CONFIRMING"
    SHUTTING_DOWN = "SHUTTING_DOWN"


class Orchestrator:
    """Orquestrador central que une todos os módulos."""

    def __init__(
        self,
        audio_pipeline: AudioPipeline,
        brain: Brain,
        executor: Executor,
        hud: HUD,
        tts: PiperTTS | None = None,
    ) -> None:
        """Inicializa o orquestrador.

        Args:
            audio_pipeline: Pipeline de áudio (Wake, VAD, STT).
            brain: Cérebro (RAG, LLM).
            executor: Executor (Segurança, Handlers).
            hud: Interface visual.
            tts: Sintetizador de voz (opcional).
        """
        self.audio = audio_pipeline
        self.brain = brain
        self.executor = executor
        self.hud = hud
        self.tts = tts

        self.state = SystemState.INITIALIZING
        self._running = False

        # Estado para confirmação de comandos HIGH risk
        self._pending_confirmation: dict[str, Any] | None = None

    def start(self) -> None:
        """Inicia o loop principal do sistema."""
        self._running = True
        self.hud.start()
        self.hud.add_log("Mascate iniciando...")

        # Configura callbacks do pipeline de áudio
        self.audio.on_activation(self._handle_wake_word)
        self.audio.on_transcription(self._handle_transcription)

        # Inicia pipeline de áudio
        self.audio.start()

        self._set_state(SystemState.IDLE)
        self.hud.add_log("Sistema pronto. Diga 'Mascate' para ativar.")
        self._speak("Mascate pronto para ajudar.")

        # Loop de espera (os eventos são tratados via callbacks)
        try:
            while self._running:
                # Aqui poderíamos processar animações no HUD ou tarefas de fundo
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        """Para o sistema de forma graciosa."""
        if self.state == SystemState.SHUTTING_DOWN:
            return

        self._set_state(SystemState.SHUTTING_DOWN)
        self._running = False

        self.hud.add_log("Encerrando sistemas...")
        self._speak("Até logo!")
        self.audio.stop()
        self.hud.stop()
        logger.info("Mascate encerrado.")

    def _set_state(self, state: SystemState) -> None:
        """Atualiza o estado interno e reflete no HUD."""
        self.state = state
        self.hud.update_state(state.value)

    def _speak(self, text: str) -> None:
        """Fala o texto usando TTS se disponível.

        Args:
            text: Texto para sintetizar e falar.
        """
        if self.tts:
            try:
                self._set_state(SystemState.SPEAKING)
                self.tts.speak(text, block=True)
            except Exception as e:
                logger.error("Erro no TTS: %s", e)
            finally:
                if self.state == SystemState.SPEAKING:
                    self._set_state(SystemState.IDLE)

    def _handle_wake_word(self) -> None:
        """Callback: Wake word detectada."""
        self._set_state(SystemState.LISTENING)
        self.hud.add_log("Ouvindo...", "WAKE")

    def _handle_transcription(self, text: str) -> None:
        """Callback: Texto transcrito disponível."""
        self._set_state(SystemState.PROCESSING)
        self.hud.add_log(f"Transcrito: '{text}'", "STT")

        # Se estamos aguardando confirmação, verifica a resposta
        if self._pending_confirmation and self.state != SystemState.CONFIRMING:
            self._handle_confirmation_response(text)
            return

        # 1. Envia para o Cérebro
        intent = self.brain.process(text)

        if not intent:
            self.hud.add_log("Nao entendi a intencao.", "ERROR")
            self._speak("Desculpe, não entendi. Pode repetir?")
            self._set_state(SystemState.IDLE)
            return

        # 2. Envia para o Executor
        self._set_state(SystemState.EXECUTING)
        self.hud.add_log(f"Executando: {intent.action}", "EXEC")

        # Converte raw_json para dict se for string
        intent_data = intent.raw_json
        if isinstance(intent_data, str):
            try:
                intent_data = json.loads(intent_data)
            except json.JSONDecodeError:
                intent_data = {
                    "action": intent.action,
                    "target": intent.target,
                    "params": intent.params,
                }

        feedback = self.executor.execute_intent(intent_data)

        # 3. Verifica se precisa de confirmação
        if feedback.startswith("CONFIRM_REQUIRED:"):
            self._request_confirmation(feedback, intent_data)
            return

        # 4. Exibe e fala o feedback
        self.hud.set_interaction(text, feedback)
        self.hud.add_log(feedback, "RESULT")
        self._speak(feedback)

        self._set_state(SystemState.IDLE)

    def _request_confirmation(self, feedback: str, intent_data: dict[str, Any]) -> None:
        """Solicita confirmação para comando HIGH risk.

        Args:
            feedback: String CONFIRM_REQUIRED:action:target
            intent_data: Dados do intent original.
        """
        parts = feedback.split(":", 2)
        action = parts[1] if len(parts) > 1 else "desconhecida"
        target = parts[2] if len(parts) > 2 else ""

        self._pending_confirmation = intent_data
        self._set_state(SystemState.CONFIRMING)

        confirmation_msg = (
            f"Confirma executar {action} em {target}? Diga 'sim' ou 'não'."
        )
        self.hud.add_log(confirmation_msg, "CONFIRM")
        self._speak(confirmation_msg)

        # Volta a ouvir para a resposta
        self._set_state(SystemState.LISTENING)

    def _handle_confirmation_response(self, text: str) -> None:
        """Processa a resposta de confirmação.

        Args:
            text: Texto transcrito (esperado: sim/não).
        """
        text_lower = text.lower().strip()
        intent_data = self._pending_confirmation
        self._pending_confirmation = None

        # Palavras de confirmação
        confirm_words = ["sim", "confirmo", "pode", "ok", "yes", "confirma", "positivo"]
        deny_words = ["nao", "não", "cancela", "cancelar", "no", "negativo", "para"]

        confirmed = any(word in text_lower for word in confirm_words)
        denied = any(word in text_lower for word in deny_words)

        if confirmed and not denied:
            self.hud.add_log("Confirmado pelo usuario", "CONFIRM")
            self._set_state(SystemState.EXECUTING)

            # Re-executa com confirmação
            feedback = self.executor.execute_intent(intent_data, confirmed=True)
            self.hud.add_log(feedback, "RESULT")
            self._speak(feedback)
        elif denied:
            feedback = "Comando cancelado."
            self.hud.add_log(feedback, "CANCEL")
            self._speak(feedback)
        else:
            feedback = "Nao entendi. Comando cancelado por seguranca."
            self.hud.add_log(feedback, "CANCEL")
            self._speak(feedback)

        self._set_state(SystemState.IDLE)
