@app.route('/api/badge/<wallet>', methods=['GET'])
def get_mining_badge(wallet):
    """Get mining status badge for a wallet in shields.io format"""
    if not wallet or not isinstance(wallet, str) or len(wallet) == 0:
        return jsonify({
            "schemaVersion": 1,
            "label": "RustChain",
            "message": "Invalid wallet",
            "color": "red"
        }), 400

    try:
        # Get balance
        with sqlite3.connect(DB_PATH) as c:
            # Try miner_pk first (old-style wallets), then miner_id (new-style)
            row = c.execute("SELECT COALESCE(amount_i64, 0) FROM balances WHERE miner_pk = ?", (wallet,)).fetchone()
            if not row or row[0] == 0:
                row = c.execute("SELECT COALESCE(amount_i64, 0) FROM balances WHERE miner_id = ?", (wallet,)).fetchone()
            balance_i64 = row[0] if row else 0
            balance_rtc = balance_i64 / 1000000.0

        # Get current epoch
        slot = current_slot()
        epoch = slot_to_epoch(slot)

        # Check if miner is active (has recent attestations)
        with sqlite3.connect(DB_PATH) as c:
            now = int(time.time())
            one_hour_ago = now - 3600
            row = c.execute(
                "SELECT COUNT(*) FROM miner_attest_recent WHERE miner = ? AND ts_ok > ?",
                (wallet, one_hour_ago)
            ).fetchone()
            is_active = bool(row and row[0] > 0)

        # Format message
        balance_str = f"{balance_rtc:.1f}" if balance_rtc >= 1 else f"{balance_rtc:.3f}"
        status_str = "Active" if is_active else "Inactive"
        message = f"{balance_str} RTC | Epoch {epoch} | {status_str}"

        # Determine color based on activity and balance
        if is_active and balance_rtc > 0:
            color = "brightgreen"
        elif is_active:
            color = "green"
        elif balance_rtc > 0:
            color = "yellow"
        else:
            color = "red"

        return jsonify({
            "schemaVersion": 1,
            "label": "RustChain",
            "message": message,
            "color": color
        })

    except Exception as e:
        return jsonify({
            "schemaVersion": 1,
            "label": "RustChain",
            "message": "Error",
            "color": "red"
        }), 500