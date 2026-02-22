@app.route('/api/badge/<wallet>', methods=['GET'])
def get_badge(wallet):
    """Get mining status badge for a wallet in shields.io format"""
    if not wallet or not wallet.strip():
        return jsonify({
            "schemaVersion": 1,
            "label": "RustChain",
            "message": "Invalid wallet",
            "color": "red"
        }), 400

    try:
        # Get balance - use safe column detection
        with sqlite3.connect(DB_PATH) as c:
            # Check which columns exist in the balances table
            cursor = c.execute("PRAGMA table_info(balances)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'miner_pk' in columns:
                query = "SELECT COALESCE(amount_i64, 0) FROM balances WHERE miner_pk = ?"
                params = (wallet,)
            elif 'miner_id' in columns:
                query = "SELECT COALESCE(amount_i64, 0) FROM balances WHERE miner_id = ?"
                params = (wallet,)
            else:
                # Neither column exists, return 0 balance
                balance_rtc = 0.0
                query = None
            
            if query:
                row = c.execute(query, params).fetchone()
                if not row:
                    balance_rtc = 0.0
                else:
                    balance_i64 = row[0] if row[0] else 0
                    balance_rtc = balance_i64 / 1000000.0

        # Get current epoch
        epoch = slot_to_epoch(current_slot())
        
        # Determine mining status based on recent activity
        is_active = False
        if balance_rtc > 0:
            # Check for recent attestations (last hour)
            with sqlite3.connect(DB_PATH) as c:
                one_hour_ago = int(time.time()) - 3600
                active_row = c.execute(
                    "SELECT 1 FROM miner_attest_recent WHERE miner = ? AND ts_ok > ?",
                    (wallet, one_hour_ago)
                ).fetchone()
                is_active = bool(active_row)
        
        # Set status and color
        if is_active and balance_rtc > 0:
            status = "Active"
            color = "brightgreen"
        elif is_active:
            status = "Active"
            color = "yellow"
        elif balance_rtc > 0:
            status = "Inactive"
            color = "orange"
        else:
            status = "Inactive"
            color = "red"

        # Format balance string
        if balance_rtc >= 1:
            balance_str = f"{balance_rtc:.1f}"
        else:
            balance_str = f"{balance_rtc:.3f}"

        message = f"{balance_str} RTC | Epoch {epoch} | {status}"

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