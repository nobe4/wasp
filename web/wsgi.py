from server import app

if __name__ == "__main__":
    try:
        port=int(os.environ.get('PORT', 8080))
    except Exception:
        port = 8080

    app.run(
            debug=True,
            host='0.0.0.0',
            port=port
            )
