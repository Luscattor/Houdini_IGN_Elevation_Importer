# Contributing to IGN Elevation Map Importer

Thank you for your interest in contributing to the IGN Elevation Map Importer! This document provides guidelines for contributing to the project.

## Code of Conduct

This project follows a professional code of conduct. Please be respectful and constructive in all interactions.

## How to Contribute

### Reporting Issues

1. **Search existing issues** before creating a new one
2. **Use the issue template** when available
3. **Provide detailed information**:
   - Operating system and version
   - Python version
   - Houdini version
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Relevant log output

### Submitting Changes

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**:
   - Follow the existing code style
   - Add tests if applicable
   - Update documentation as needed
4. **Test your changes**:
   - Verify the downloader works with sample data
   - Test Houdini integration if modified
5. **Commit with clear messages**:
   ```bash
   git commit -m "Add feature: brief description"
   ```
6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Create a Pull Request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/IGN_Elevation_Importer.git
cd IGN_Elevation_Importer

# Install development dependencies (optional)
pip install -r requirements.txt

# Run tests (if available)
python -m pytest tests/
```

## Coding Standards

### Python Code Style
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and concise

### Documentation
- Update README.md for user-facing changes
- Update WORKFLOW.md for process changes
- Add inline comments for complex logic
- Include examples in docstrings

### Commit Messages
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests when applicable

## Areas for Contribution

### High Priority
- **Error handling improvements**
- **Performance optimizations**
- **Cross-platform compatibility**
- **Additional coordinate system support**

### Medium Priority
- **GUI interface for configuration**
- **Batch processing tools**
- **Advanced filtering options**
- **Integration with other DCC software**

### Documentation
- **Video tutorials**
- **Advanced workflow examples**
- **Troubleshooting guides**
- **API documentation**

## Testing

### Manual Testing
1. Test with various tile configurations
2. Verify Houdini integration works
3. Check cross-platform compatibility
4. Validate with different IGN data sources

### Automated Testing (Future)
- Unit tests for parsing functions
- Integration tests for download process
- Houdini Python SOP validation

## Release Process

### Version Numbering
We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist
- [ ] Update version numbers
- [ ] Update CHANGELOG.md
- [ ] Test with latest Houdini version
- [ ] Verify documentation is current
- [ ] Create release notes

## Questions and Support

- **General questions**: Use GitHub Discussions
- **Bug reports**: Use GitHub Issues
- **Feature requests**: Use GitHub Issues with "enhancement" label
- **Professional support**: Contact maintainers directly

## Recognition

Contributors will be acknowledged in:
- README.md contributors section
- Release notes for significant contributions
- Project documentation where applicable

Thank you for helping make this tool better for the VFX and game development community!

---

*This contributing guide is based on industry best practices for open-source projects.*