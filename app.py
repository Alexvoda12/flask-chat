from flask import Flask, render_template, send_file, request, session, redirect, url_for
import random
import g4f

app = Flask(__name__)
app.secret_key = 'qwery1'  # Необходимо для работы сессий your_secret_key_here

# Инициализация истории чата в сессии
def init_chat_history():
    if 'chat_history' not in session:
        session['chat_history'] = []

@app.route('/')
@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Neural Network Platform</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                text-align: center;
            }
            h1 {
                color: #6aa8cc;
            }
            .services {
                display: flex;
                justify-content: center;
                gap: 30px;
                margin-top: 40px;
            }
            .service-card {
                background-color: #b8e0ff;
                border-radius: 10px;
                padding: 20px;
                width: 200px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            .service-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            }
            .service-card a {
                text-decoration: none;
                color: #29b0ff;
                font-weight: bold;
                font-size: 18px;
            }
            .service-card p {
                color: #6e42ff;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <h1>Welcome to the Neural Network Platform</h1>
        <p>Choose one of the available services:</p>
        
        <div class="services">
            <div class="service-card">
                <a href="/img">Image Generation</a>
                <p>Create amazing AI-generated images</p>
            </div>
            
            <div class="service-card">
                <a href="/chat">Chat with AI</a>
                <p>Have a conversation with our smart assistant</p>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/img', methods=['GET', 'POST'])
def img_form():
    if request.method == 'POST':
        # Получаем данные из формы
        prompt = request.form['prompt'].replace(' ', '%20')
        print(request.form)
        count = int(request.form['count'])
        width = request.form['width']
        height = request.form['height']
        # Перенаправляем на страницу с результатами
        return expansion_pack(prompt, count, width, height)
    
    # Если GET запрос - показываем форму
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Image Generator</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }
            form { display: grid; gap: 15px; }
            input, button { padding: 8px; font-size: 16px; }
            button { background-color: #4CAF50; color: white; border: none; cursor: pointer; }
            button:hover { background-color: #45a049; }
        </style>
    </head>
    <body>
        <h1>Image Generator</h1>
        <form method="post">
            <label for="prompt">Prompt:</label>
            <input type="text" id="prompt" name="prompt" required>
            
            <label for="count">Count (1-10000):</label>
            <input type="number" id="count" name="count" min="1" max="10000" value="1" required>
            
            <input id="remember" type="checkbox" name="remember">

            <label for="width">Width:</label>
            <input type="text" id="width" name="width" value="1024" required>
            
            <label for="height">Height:</label>
            <input type="text" id="height" name="height" value="1024" required>
            
            <button type="submit">Generate Images</button>
        </form>
    </body>
    </html>
    '''

@app.route('/img/<int:count>/<width>:<height>/<prompt>')
def expansion_pack(prompt, count, width, height):
    response = f"""<head>
        <title>{count} images: {prompt.replace('%20', ' ')}</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
            img {{ max-width: 100%; margin-bottom: 20px; border: 1px solid #ddd; }}
            .back-link {{ display: inline-block; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <a href="/img" class="back-link">← Back to generator</a>
        <h1>{count} images: {prompt.replace('%20', ' ')}</h1>\n"""
    
    for i in range(count):
        try:
            url = f"https://image.pollinations.ai/prompt/{prompt}?width={width}&height={height}&model=Flux&nologo=true&private=false&enhance=false&safe=false&referrer=https://g4f.dev/&seed={random.randint(0, 100000000)}"
            print(url)
            response += f"""<img src="{url}" alt="Generated Image {i+1}">\n"""
        except Exception as e:
            response += f"<p>Error generating image: {str(e)}</p>"
    
    response += "</body>"
    return response

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    init_chat_history()

    if request.method == 'POST':
        # Проверяем, была ли нажата кнопка очистки
        if 'clear_chat' in request.form:
            session['chat_history'] = []
            session.modified = True
            return redirect(url_for('chat'))
        
        # Обработка обычного сообщения
        user_message = request.form['message']
        if user_message.strip():
            # Добавляем сообщение пользователя в историю
            session['chat_history'].append({'role': 'user', 'content': user_message})
            
            try:
                # Получаем ответ от нейросети
                response = g4f.ChatCompletion.create(
                    model=g4f.models.gpt_4,
                    messages=session['chat_history'],
                    # provider=g4f.Provider.Bing
                )
                
                # Добавляем ответ нейросети в историю
                session['chat_history'].append({'role': 'assistant', 'content': response})
                session.modified = True  # Убедимся, что сессия сохранится
            except Exception as e:
                session['chat_history'].append({'role': 'assistant', 'content': f"Error: {str(e)}"})
                session.modified = True
    
    # Отображаем чат
    return render_template('chat.html', chat_history=session['chat_history'])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=2012)