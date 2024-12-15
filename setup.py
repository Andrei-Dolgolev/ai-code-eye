from setuptools import find_packages, setup

AI_CODE_EYE_VERSION = "0.1.0"

long_description = """
# AI Code Eye
"""
try:
    with open("README.md", "r", encoding="utf-8") as ifp:
        long_description = ifp.read()
except FileNotFoundError:
    pass

setup(
    name="ai-code-eye",
    version=AI_CODE_EYE_VERSION,
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "requests>=2.20.0",
        "typer>=0.9.0",
        "rich>=13.0.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "black",
            "isort",
            "mypy",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "types-requests",
        ],
        "distribute": [
            "setuptools",
            "twine",
            "wheel",
        ],
    },
    package_data={
        "ai_code_eye": ["py.typed"]
    },
    zip_safe=False,
    description="CLI tool for AI-based code translation from one language to another.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Andrey Dolgolev",
    author_email="andrey@simiotics.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: Code Generators",
    ],
    url="https://github.com/yourusername/ai-code-eye",
    entry_points={
        "console_scripts": [
            "ai-code-eye=ai_code_eye.cli:app",
        ]
    },
)
