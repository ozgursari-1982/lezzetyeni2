from app import create_app
import os
from dotenv import load_dotenv

# Environment variables'ı yükle
load_dotenv()

# Uygulama instance'ını oluştur
app = create_app()

if __name__ == '__main__':
    # Debug modu ve port konfigürasyon
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    port = int(os.environ.get('PORT', 5002))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"Starting Restaurant Reservation System...")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"Debug Mode: {debug_mode}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"URL: http://{host}:{port}")
    print("\nDefault login credentials:")
    print("Username: admin")
    print("Password: admin123")
    print("\n" + "="*50)
    
    app.run(debug=debug_mode, host=host, port=port)