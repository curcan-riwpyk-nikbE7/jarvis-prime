import math
import numpy as np
import pygame

class SoundFX:
    """Генератор кинематографичных звуковых эффектов Тони Старка в реальном времени"""
    _initialized = False

    @classmethod
    def init(cls):
        if not cls._initialized:
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                cls._initialized = True
            except Exception:
                pass

    @classmethod
    def play_startup_sound(cls):
        """Звук включения реактора Джарвиса (нарастающий футуристичный свист с басом)"""
        cls.init()
        try:
            sample_rate = 44100
            duration = 0.8
            n_samples = int(sample_rate * duration)
            t = np.linspace(0, duration, n_samples, False)

            # Нарастающая частота от 120 Гц до 880 Гц (эффект заряда реактора)
            freq = np.linspace(120, 880, n_samples)
            wave = 0.4 * np.sin(2 * np.pi * freq * t)

            # Плавное появление и затухание
            fade = np.linspace(0, 1, int(sample_rate * 0.1))
            wave[:len(fade)] *= fade
            wave[-len(fade):] *= fade[::-1]

            audio = (wave * 32767).astype(np.int16)
            stereo = np.column_stack((audio, audio))
            sound = pygame.sndarray.make_sound(stereo)
            sound.play()
        except Exception:
            pass

    @classmethod
    def play_wake_sound(cls):
        """Звуковой пинг готовности слушать (двойной короткий неоновый сигнал)"""
        cls.init()
        try:
            sample_rate = 44100
            duration = 0.12
            n_samples = int(sample_rate * duration)
            t = np.linspace(0, duration, n_samples, False)
            wave = 0.3 * np.sin(2 * np.pi * 960 * t)
            
            fade = np.linspace(1, 0, n_samples)
            wave *= fade

            audio = (wave * 32767).astype(np.int16)
            stereo = np.column_stack((audio, audio))
            sound = pygame.sndarray.make_sound(stereo)
            sound.play()
        except Exception:
            pass
