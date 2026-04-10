# Space Shooter

Gioco arcade space shooter sviluppato in Python con pygame come progetto universitario.

## Come si gioca

- **Frecce** o **WASD** per muovere la navicella
- La navicella **spara automaticamente**
- Evita i nemici e sopravvivi il più a lungo possibile

## Tipi di nemici

| Colore | HP | Punti |
|--------|----|-------|
| Rosso  | 1  | 10    |
| Arancione | 1 | 15  |
| Viola  | 3  | 30    |

Guadagni anche **1 punto** per ogni nemico che supera lo schermo senza colpirti.

## Installazione

```bash
pip install -r requirements.txt
python main.py
```

## Struttura del progetto

```
space-shooter/
├── main.py         # Entry point e game loop
├── settings.py     # Costanti e configurazione
├── player.py       # Classe Player
├── enemy.py        # Classe Enemy
├── bullet.py       # Classe Bullet
├── particle.py     # Classe Particle (effetti esplosione)
├── star.py         # Classe Star (sfondo animato)
├── hud.py          # Interfaccia utente (punteggio, vite)
└── requirements.txt
```

## Requisiti

- Python 3.13+
- pygame 2.6.1
