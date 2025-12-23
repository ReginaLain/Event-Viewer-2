import win32evtlog
import win32evtlogutil
import win32security
import win32con
from flask import Flask, render_template, jsonify, send_from_directory
import json
import os
import sys

# Point Flask to the built frontend
base_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(base_dir, "frontend", "dist")

app = Flask(__name__, 
            static_folder=os.path.join(frontend_dir, "assets"),
            template_folder=frontend_dir)

def resolve_sid(sid):
    try:
        name, domain, type = win32security.LookupAccountSid(None, sid)
        return f"{domain}\\{name}"
    except:
        return "N/A"

def get_event_logs(log_type="System", limit=200):
    server = 'localhost'
    try:
        hand = win32evtlog.OpenEventLog(server, log_type)
    except Exception as e:
        return [{"source": "System", "type": "Error", "time": "", "event_id": 0, "details": f"Failed to open log: {str(e)}"}]

    flags = win32evtlog.EVENTLOG_BACKWARDS_READ|win32evtlog.EVENTLOG_SEQUENTIAL_READ
    total = 0
    events = []
    
    while True:
        try:
            events_list = win32evtlog.ReadEventLog(hand, flags, 0)
            if not events_list:
                break
                
            for event in events_list:
                # Map event type
                evt_type = "Unknown"
                if event.EventType == win32con.EVENTLOG_ERROR_TYPE:
                    evt_type = "Error"
                elif event.EventType == win32con.EVENTLOG_WARNING_TYPE:
                    evt_type = "Warning"
                elif event.EventType == win32con.EVENTLOG_INFORMATION_TYPE:
                    evt_type = "Information"
                elif event.EventType == win32con.EVENTLOG_AUDIT_SUCCESS:
                    evt_type = "Success Audit"
                elif event.EventType == win32con.EVENTLOG_AUDIT_FAILURE:
                    evt_type = "Failure Audit"
                
                try:
                    msg = win32evtlogutil.SafeFormatMessage(event, log_type)
                except:
                    msg = None
                
                if not msg:
                    if event.StringInserts:
                        msg = ", ".join(event.StringInserts)
                    else:
                        msg = "No description available"

                user_str = "N/A"
                if event.Sid is not None:
                    user_str = resolve_sid(event.Sid)

                events.append({
                    "source": event.SourceName,
                    "event_id": event.EventID & 0xFFFF,
                    "type": evt_type,
                    "time": str(event.TimeGenerated),
                    "category": event.EventCategory,
                    "details": msg,
                    "user": user_str,
                    "computer": event.ComputerName,
                    "log_name": log_type
                })
                
                total += 1
                if total >= limit:
                    break
        except Exception as e:
            break
            
        if total >= limit:
            break
            
    win32evtlog.CloseEventLog(hand)
    return events

def clear_event_log(log_type):
    server = 'localhost'
    try:
        hand = win32evtlog.OpenEventLog(server, log_type)
        win32evtlog.ClearEventLog(hand, None)
        win32evtlog.CloseEventLog(hand)
        return True, "Log cleared successfully"
    except Exception as e:
        return False, f"Failed to clear log (No Admin?): {str(e)}"

# Routing
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/assets/<path:path>')
def send_assets(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/logs/<log_type>')
def api_logs(log_type):
    valid_logs = ['Application', 'System', 'Security', 'Setup']
    if log_type not in valid_logs:
        return jsonify({"error": "Invalid log type"}), 400
    events = get_event_logs(log_type=log_type)
    return jsonify(events)

@app.route('/api/logs/<log_type>/clear', methods=['POST'])
def api_clear_logs(log_type):
    valid_logs = ['Application', 'System', 'Security', 'Setup']
    if log_type not in valid_logs:
        return jsonify({"error": "Invalid log type"}), 400
    success, msg = clear_event_log(log_type)
    if success:
        return jsonify({"status": "success", "message": msg})
    else:
        return jsonify({"error": msg}), 500

if __name__ == '__main__':
    print("----------------------------------------")
    print("EventViewer Pro is starting...")
    print("Open your browser at: http://127.0.0.1:5000")
    print("----------------------------------------")
    import webbrowser
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=False, port=5000)
