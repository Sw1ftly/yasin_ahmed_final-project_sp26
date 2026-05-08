import os
import sys
import time
import hashlib
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.retrain import train_model

WATCH_PATH   = 'data/'
STATE_FILE   = 'ml/monitor_state.txt'
POLL_SECONDS = 30


def _get_dir_hash(path):
    """Hash the names and sizes of all files in the watched folder."""
    if not os.path.exists(path):
        return ''
    h = hashlib.md5()
    for fname in sorted(os.listdir(path)):
        fpath = os.path.join(path, fname)
        if os.path.isfile(fpath):
            h.update(fname.encode())
            h.update(str(os.path.getsize(fpath)).encode())
    return h.hexdigest()


def _read_last_hash():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return f.read().strip()
    return ''


def _write_hash(h):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        f.write(h)


def run_monitor(once=False):
    print(f'Pipeline monitor started. Watching: {WATCH_PATH}')
    while True:
        current = _get_dir_hash(WATCH_PATH)
        last    = _read_last_hash()
        if current and current != last:
            print('Change detected in data folder — triggering re-train...')
            success, auc, version = train_model()
            if success:
                print(f'Re-training complete. New version: {version}')
            _write_hash(current)
        else:
            print(f'No changes detected in {WATCH_PATH}.')
        if once:
            break
        print(f'Sleeping {POLL_SECONDS}s...')
        time.sleep(POLL_SECONDS)


if __name__ == '__main__':
    run_monitor()
