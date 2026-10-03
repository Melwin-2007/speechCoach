import json
import argparse
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from speechcoach.audio.io import load_audio
from speechcoach.features.frame import frame_features
from speechcoach.features.words import word_table

def main():
    parser = argparse.ArgumentParser(description="Plot acoustic features of an audio file")
    parser.add_argument("audio_path", type=Path)
    parser.add_argument("alignment_path", type=Path, help="JSON file with word alignments")
    args = parser.parse_args()
    
    print(f"Loading {args.audio_path}...")
    y = load_audio(args.audio_path)
    
    print("Extracting frame features (may take a moment)...")
    g = frame_features(y)
    
    print(f"Loading alignments from {args.alignment_path}...")
    with open(args.alignment_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print("Aggregating word stats...")
    words = word_table(data['words'], g)
    
    print("Rendering plot...")
    fig, axs = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
    
    t = g['t']
    
    # 1. Pitch
    axs[0].plot(t, g['st'], color='blue', label='Pitch (st)')
    axs[0].set_ylabel('Semitones')
    axs[0].set_title('Pitch over Time')
    axs[0].grid(True, alpha=0.3)
    
    # 2. Energy
    axs[1].plot(t, g['db_rel'], color='orange', label='Energy (db_rel)')
    axs[1].set_ylabel('Relative dB')
    axs[1].set_title('Energy over Time')
    axs[1].grid(True, alpha=0.3)
    
    # 3. Pauses (Bar plot of pause_before for each word)
    word_times = [w['start'] for w in words]
    pauses = [w['pause_before'] for w in words]
    axs[2].bar(word_times, pauses, width=0.1, color='red', align='edge')
    axs[2].set_ylabel('Pause Duration (s)')
    axs[2].set_xlabel('Time (s)')
    axs[2].set_title('Pauses Before Words')
    axs[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
