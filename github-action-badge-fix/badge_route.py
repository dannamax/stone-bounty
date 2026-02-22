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
                # Fallback: no balance data available
                balance_rtc = 0.0
            
            if 'miner_pk' in columns or 'miner_id' in columns:
                row = c.execute(query, params).fetchone()
                if not row:
                    balance_rtc = 0.0
                else:
                    balance_i64 = row[0] if row[0] else 0
                    balance_rtc = balance_i64 / 1000000.0

        # Get current epoch
        epoch = slot_to_epoch(current_slot())
        
        # Determine mining status
        if balance_rtc > 0:
            status = "Active"
            color = "brightgreen"
        else:
            status = "Inactive"
            color = "red"

        message = f"{balance_rtc:.1f} RTC | Epoch {epoch} | {status}"

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