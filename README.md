
# 🎓 LearnMate AI

> Your Smart Study Companion powered by Google Gemini AI

---

## 📌 Overview

**LearnMate AI** is an intelligent, all-in-one study assistant that transforms how students engage with learning content. Whether it's a single topic, an entire chapter, or a full textbook, LearnMate AI uses the power of Google's Gemini API to generate:

- ✅ In-depth explanations
- ✅ Crisp summaries
- ✅ Well-organized study notes
- ✅ AI-generated images to visualize concepts
- ✅ Natural audio narrations
- ✅ Learning history & tracking

Built with **Streamlit**, it offers a smooth, interactive, and visually appealing learning experience. Perfect for self-study, revision, and quick concept clarity.

---

## 🚀 Features

### 📚 Content Generation
- **Topic-Based Input**: Enter any topic/chapter/book name.
- **Explanations**: Get detailed, easy-to-understand responses.
- **Summaries**: Short, concise highlights for quick revision.
- **Notes**: Neatly formatted, point-wise notes for effective retention.

### 🧠 Multimodal Learning
- **Audio Narration**: Converts content to natural speech using Google Text-to-Speech (TTS).
- **AI Images**: Generates images for better visualization using Gemini's image capabilities.

### 🧾 Study History
- View all previously entered topics.
- Revisit generated content for each topic.

### 🌓 Accessibility
- **Dark Mode / Light Mode**
- **Adjustable Font Sizes**

---

## 🖼️ Screenshots

> Add screenshots here after running the app

---

## 🛠️ Tech Stack

- **Frontend/UI**: [Streamlit](https://streamlit.io/)
- **AI/ML API**: [Gemini API by Google](https://ai.google.dev/)
- **TTS**: Google Text-to-Speech
- **Image Generation**: Gemini's vision capabilities
- **Storage**: JSON files or SQLite (depending on implementation)

---

## 🧑‍💻 How to Run the App

### 1. **Clone the Repository**
```bash
git clone https://github.com/your-username/learnmate-ai.git
cd learnmate-ai
````

### 2. **Create a Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 4. **Set Environment Variables**

Create a `.env` file in the root directory and add your Gemini API key:

```
GEMINI_API_KEY=your_api_key_here
```

### 5. **Run the App**

```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
learnmate-ai/
│
├── app.py                  # Main Streamlit app
├── utils.py                # Helper functions (API calls, audio, image, etc.)
├── requirements.txt        # List of dependencies
├── .env                    # Environment file for API key
├── history.json            # Stores user history
└── README.md               # You're reading it!
```

---

## 🌱 Future Enhancements

* 🔁 Add interactive quizzes and MCQs
* 🗃️ Store history in a database (e.g., SQLite or Firebase)
* 🔒 User login and personalization
* 📊 Analytics dashboard to track progress
* 🌐 Support for multiple languages

---

## 🤝 Contributing

Pull requests are welcome! If you’d like to contribute:

1. Fork the repo
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Create a new Pull Request

---

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 💬 Contact

For queries or collaborations:

**Pranit Chilbule**
📧 Email: [pranit@example.com](mailto:pranit@example.com)
📱 LinkedIn: [linkedin.com/in/pranit](https://linkedin.com/in/pranit)

---

> “Education is not the learning of facts, but the training of the mind to think.” – Albert Einstein

```

---

Would you like a `requirements.txt` and sample `.env` file generated as well?
```
