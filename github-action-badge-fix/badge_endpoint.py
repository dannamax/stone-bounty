@app.route('/api/badge/<wallet>', methods=['GET'])
def api_badge(wallet):
    """Return mining status badge in shields.io format for GitHub Action"""
    if not wallet or not wallet.strip():
        return jsonify({
            "schemaVersion": 1,
            "label": "RustChain",
            "message": "Invalid wallet",
            "color": "red"
        }), 400
    
    try:
        # Get wallet balance safely
        with sqlite3.connect(DB_PATH) as c:
            # Check which columns exist in the balances table
            cursor = c.execute("PRAGMA table_info(balances)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'miner_pk' in columns:
                query = "SELECT amount_i64 FROM balances WHERE miner_pk = ?"
            elif 'miner_id' in columns:
                query = "SELECT amount_i64 FROM balances WHERE miner_id = ?"
            else:
                # If neither column exists, assume no balance
                balance_rtc = 0.0
                query = None
            
            if query:
                row = c.execute(query, (wallet,)).fetchone()
                if row and row[0] is not None:
                    balance_rtc = float(row[0]) / 1000000.0
                else:
                    balance_rtc = 0.0
            else:
                balance_rtc = 0.0
            
            # Get current epoch
            epoch = slot_to_epoch(current_slot())
            
            # Check if wallet is actively mining (has recent attestations)
            now = int(time.time())
            one_hour_ago = now - 3600
            active_row = c.execute(
                "SELECT 1 FROM miner_attest_recent WHERE miner = ? AND ts_ok > ?", 
                (wallet, one_hour_ago)
            ).fetchone()
            is_active = bool(active_row)
            
            # Format message
            balance_str = f"{balance_rtc:.1f}" if balance_rtc >= 1 else f"{balance_rtc:.3f}"
            status = "Active" if is_active else "Inactive"
            message = f"{balance_str} RTC | Epoch {epoch} | {status}"
            
            # Determine color based on activity and balance
            if is_active and balance_rtc > 0:
                color = "brightgreen"
            elif is_active:
                color = "yellow"
            elif balance_rtc > 0:
                color = "orange"
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