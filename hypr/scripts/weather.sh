#!/bin/bash
CACHE_FILE="/tmp/hyprlock_weather.cache"
BACKUP_FILE="$HOME/.cache/hyprlock_weather_last"

mkdir -p "$HOME/.cache"

DATA=$(curl -m 3 -s "https://api.open-meteo.com/v1/forecast?latitude=38.73&longitude=35.48&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=auto&forecast_days=4" 2>/dev/null)

if [ -n "$DATA" ] && echo "$DATA" | jq -e '.daily.time[0]' &>/dev/null; then
    # Sadece 4 günü (0..3) alıyoruz ve aralarına birer boş satır ekliyoruz
    CLEAN=$(echo "$DATA" | jq -r '
      def icon(c):
        if c == 0 then "☀️"
        elif c <= 3 then "⛅"
        elif c <= 48 then "🌫️"
        elif c <= 67 then "🌧️"
        elif c <= 77 then "❄️"
        elif c <= 82 then "🌦️"
        elif c <= 86 then "🌨️"
        else "⚡"
        end;
      .daily as $d |
      [ range(0; 4) | "\($d.time[.] | strptime("%Y-%m-%d") | strftime("%a")): \(icon($d.weather_code[.])) \($d.temperature_2m_min[.] | round)°C / \($d.temperature_2m_max[.] | round)°C" ] | join("\n\n")
    ')

    echo "$CLEAN" > "$CACHE_FILE"
    echo "$CLEAN" > "$BACKUP_FILE"
    echo "$CLEAN"
else
    if [ -s "$BACKUP_FILE" ]; then
        cat "$BACKUP_FILE"
    elif [ -s "$CACHE_FILE" ]; then
        cat "$CACHE_FILE"
    else
        echo "Hava durumu alınıyor..."
    fi
fi
