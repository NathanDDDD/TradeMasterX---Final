# Contributing to TradeMasterX

Thank you for your interest in contributing to TradeMasterX! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- Git
- Basic understanding of trading concepts

### Setup Development Environment
1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/TradeMasterX---Final.git
   cd TradeMasterX---Final
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 📝 Development Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all classes and functions
- Keep functions small and focused

### Testing
- Write unit tests for new features
- Ensure all tests pass before submitting
- Run tests with:
  ```bash
  PYTHONPATH=TradeMasterX python -m unittest discover -s TradeMasterX/tests
  ```

### Adding New Analyzers
1. Create a new file in `trademasterx/core/analyzers/`
2. Implement the `analyze(data)` method
3. Add the analyzer to `MasterBot.__init__()`
4. Write tests for the new analyzer
5. Update documentation

### Adding New Features
1. Create feature branch: `git checkout -b feature/your-feature-name`
2. Implement the feature
3. Add tests
4. Update documentation
5. Submit a pull request

## 🔧 Project Structure

```
TradeMasterX/
├── trademasterx/           # Main package
│   ├── core/              # Core trading logic
│   │   ├── analyzers/     # Market analysis modules
│   │   ├── masterbot.py   # Main trading bot
│   │   └── ...
│   └── utils/             # Utility functions
├── tests/                 # Unit tests
├── dashboard.py           # Streamlit dashboard
├── launch.py              # CLI launcher
└── requirements.txt       # Dependencies
```

## 🐛 Reporting Issues

When reporting issues, please include:
- **Description** of the problem
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Error messages** or logs

## 📋 Pull Request Process

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests** for new functionality
5. **Update documentation** if needed
6. **Run tests** to ensure everything works
7. **Submit a pull request** with a clear description

### Pull Request Guidelines
- Use clear, descriptive commit messages
- Include tests for new features
- Update documentation as needed
- Reference any related issues

## 🎯 Areas for Contribution

### High Priority
- **New Analyzers**: Add more technical analysis indicators
- **Risk Management**: Implement position sizing and stop-loss logic
- **Performance Optimization**: Improve speed and efficiency
- **Testing**: Add more comprehensive test coverage

### Medium Priority
- **UI Improvements**: Enhance the Streamlit dashboard
- **Documentation**: Improve guides and examples
- **Error Handling**: Better error messages and recovery
- **Logging**: Enhanced logging and monitoring

### Low Priority
- **New Exchanges**: Support for additional trading platforms
- **Advanced Features**: Machine learning integration
- **Mobile Support**: Mobile-friendly dashboard
- **Internationalization**: Multi-language support

## 📞 Getting Help

- **Issues**: Use GitHub Issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Documentation**: Check the README and inline code comments

## 📄 License

By contributing to TradeMasterX, you agree that your contributions will be licensed under the same license as the project.

## 🙏 Recognition

Contributors will be recognized in:
- The project README
- Release notes
- GitHub contributors page

Thank you for contributing to TradeMasterX! 🚀 