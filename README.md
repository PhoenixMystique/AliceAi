<div align="center">

# 🤖 AliceJobSeeker

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/Selenium-4.0+-green.svg)](https://www.selenium.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)](https://github.com/yourusername/AliceJobSeeker)

**Your AI-powered job application assistant that automates the boring parts of job hunting**

<img src="https://i.imgur.com/YourLogoHere.png" alt="AliceJobSeeker Logo" width="200"/>

</div>

## ✨ Features

- 🔍 **Automated Job Discovery** - Find jobs matching your preferences automatically
- ✅ **Smart Filtering** - AI-powered job preference matching
- 🤝 **Automated Applications** - Handle job applications with dynamic Q&A
- 📊 **Detailed Logging** - Keep track of all applications and their status
- 🔄 **Resume Parsing** - Automatically extract data from your resume
- 🌐 **Multi-site Support** - Currently supports Naukri.com (with more coming soon!)

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Chrome browser
- Gemini API key (for AI-powered features)

### Installation

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/AliceJobSeeker.git
cd AliceJobSeeker
```

2. **Create and activate a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Configure your environment:**
   - Add your resume PDF file to the `./resume/` folder
   - Edit `customization.json` with your preferences and API key

5. **Run the job seeker:**

```bash
python main.py
```

## ⚙️ Configuration

AliceJobSeeker is highly customizable. Edit the `customization.json` file to:

- Set your job search URL (currently focused on Naukri.com)
- Configure job preferences
- Set default answers for common questions
- Customize browser settings
- Set up Gemini AI parameters
- Configure logging options

Example configuration:

```json
{
  "job_search_url": "https://www.naukri.com/graphic-designer-jobs-in-noida",
  "job_preferences": "Graphic designer related job",
  "gemini_api_key": "YOUR_API_KEY",
  "default_answers": {
    "notice_period": "0 days (Immediate)",
    "expected_salary": "6 LPA",
    "current_salary": "4.5 LPA"
    // ...other answers
  }
  // ...other settings
}
```

## 📝 How It Works

1. **Discovery**: AliceJobSeeker navigates to job search pages and finds job listings
2. **Filtering**: It uses AI to determine if jobs match your preferences
3. **Application**: For matching jobs, it attempts to apply automatically
4. **Q&A**: Handles application questions using AI, with fallbacks to predefined answers
5. **Logging**: Records all activities for your review

## 🛣️ Roadmap & TODO

- [ ] **LinkedIn Integration**: Add support for job discovery and application on LinkedIn
- [ ] **Instahyre Support**: Expand to support Instahyre's job application process
- [ ] **Multi-language Resume Support**: Parse and utilize resumes in different languages
- [ ] **Enhanced AI Matching**: Improve the job preference matching algorithm
- [ ] **Dashboard Interface**: Create a web-based dashboard for monitoring and control
- [ ] **Mobile Notifications**: Receive alerts about successful applications

## 👥 Contribution

Contributions are much awaited and highly appreciated! Here's how you can contribute:

1. Fork the repository
2. Create your feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Open a pull request

Areas especially looking for help:
- Additional job site integrations
- UI/UX improvements
- Test coverage
- Documentation

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- Selenium WebDriver
- Google Gemini API
- PyPDF2 and pdfplumber for resume parsing
- All our amazing contributors!

---

<div align="center">

**Made with ❤️**

</div>
