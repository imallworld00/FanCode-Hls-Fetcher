import os
import requests
from flask import Flask, jsonify, Response, request

app = Flask(__name__)

FANCODE_REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN", "আপনার_ফ্যানকোড_রিফ্রেশ_টোকেন_এখানে_দিন")

def get_live_fancode_streams():
    """ফ্যানকোড সার্ভার থেকে রিয়েল-টাইমে লাইভ ম্যাচের লিস্ট স্ক্র্যাপ করার ফাংশন"""
    try:
        headers = {
            "Authorization": f"Bearer {FANCODE_REFRESH_TOKEN}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # ফ্যানকোডের আসল লাইভ ম্যাচ এপিআই (কাল্পনিক এন্ডপয়েন্ট)
        api_url = "https://fancode.com" 
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json() 
        else:
            # এপিআই রেসপন্স না দিলে ডেমো হিসেবে ফুটবল ও ক্রিকেট দুটি ম্যাচই রিটার্ন করবে টেস্ট করার জন্য
            return [
                {
                    "title": "Real Madrid vs Barcelona",
                    "type": "football",
                    "thumbnail": "https://example.com",
                    "stream_url": "https://google.com"
                },
                {
                    "title": "Bangladesh vs India Cricket",
                    "type": "cricket",
                    "thumbnail": "https://example.com",
                    "stream_url": "https://google.com"
                }
            ]
            
    except Exception as e:
        return [
            {
                "title": "Real Madrid vs Barcelona",
                "type": "football",
                "thumbnail": "https://example.com",
                "stream_url": "https://google.com"
            },
            {
                "title": "Bangladesh vs India Cricket",
                "type": "cricket",
                "thumbnail": "https://example.com",
                "stream_url": "https://google.com"
            }
        ]

@app.route('/')
def home():
    return jsonify({"status": "Server is running", "modes": ["/matches", "/playlist.m3u"]})

@app.route('/matches')
def matches():
    """অ্যাডমিন প্যানেলের জন্য ফিল্টারযুক্ত JSON API এন্ডপয়েন্ট"""
    data = get_live_fancode_streams()
    
    # URL থেকে 'search' কী-ওয়ার্ড খুঁজে বের করবে (যেমন: ?search=football)
    search_query = request.args.get('search', '').lower()
    
    if search_query and isinstance(data, list):
        # ইউজারের সার্চ কি-ওয়ার্ডের সাথে মিলিয়ে ম্যাচ ফিল্টার করবে
        filtered_matches = [
            match for match in data 
            if search_query in match.get("title", "").lower() or search_query in match.get("type", "").lower()
        ]
        return jsonify(filtered_matches)
        
    return jsonify(data)

@app.route('/playlist.m3u')
def playlist():
    """IPTV বা অটো-আপডেটেড M3U প্লেলিস্ট"""
    data = get_live_fancode_streams()
    
    m3u_content = "#EXTM3U\n"
    if isinstance(data, list):
        for match in data:
            match_name = match.get("title", "Live Match")
            logo = match.get("thumbnail", "")
            stream_url = match.get("stream_url", "")
            
            m3u_content += f'#EXTINF:-1 tvg-logo="{logo}",{match_name}\n{stream_url}\n'
    else:
        m3u_content += "#EXTINF:-1, No Active Matches Right Now\nhttp://example.com\n"
        
    return Response(m3u_content, mimetype='text/plain')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
