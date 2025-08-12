"""
Script to remove emojis from agent files for Windows compatibility
"""
import os
import re

def remove_emojis_from_file(filepath):
    """Remove emojis from a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace specific emojis with text equivalents
    replacements = {
        '🔥🔥🔥': '***',
        '🔥': '*',
        '🎯': '[TARGET]',
        '📊': '[STATS]',
        '💰': '[VALUE]',
        '💡': '[TIP]',
        '🏀': '[NBA]',
        '📈': '[UP]',
        '📉': '[DOWN]',
        '🎲': '[DICE]',
        '📋': '[LIST]',
        '📄': '[DOC]',
        '✨': '*',
        '🌟': '*',
        '🏆': '[WINNER]',
        '🚀': '[ROCKET]',
        '💪': '[STRONG]',
        '⚡': '[FAST]',
        '🎮': '[GAME]',
        '🏅': '[MEDAL]',
        '🔮': '[PREDICT]',
        '🎉': '!!!',
        '✅': '[OK]',
        '❌': '[X]',
        '⏳': '[WAIT]',
        '⚠️': '[WARNING]',
    }
    
    original = content
    for emoji, replacement in replacements.items():
        content = content.replace(emoji, replacement)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")
        return True
    return False

def main():
    """Remove emojis from all agent files"""
    agent_dir = 'app/agents'
    files_updated = 0
    
    for filename in os.listdir(agent_dir):
        if filename.endswith('.py'):
            filepath = os.path.join(agent_dir, filename)
            if remove_emojis_from_file(filepath):
                files_updated += 1
    
    print(f"\nTotal files updated: {files_updated}")

if __name__ == "__main__":
    main()