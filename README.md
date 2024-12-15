# AI Code Eye 👁️ (Eye) + 🤖 (AI) = 👁️🤖

AI Code Eye is a CLI tool that translates code from one programming language to another using AI technology.

## Installation

```bash
pip install ai-code-eye
```

## Usage

Set your OpenAI API key:
```bash
export OPENAI_API_KEY=your-api-key-here
```

### Basic Command

```bash
ai-code-eye translate <source_dir> <output_dir> --source-lang <lang1> --target-lang <lang2>
```

### Examples

Translate Java to JavaScript:
```bash
ai-code-eye translate examples/java_to_js/src ./output --source-lang java --target-lang javascript
```

Translate Python to TypeScript:
```bash
ai-code-eye translate examples/python_to_ts/src ./output --source-lang python --target-lang typescript
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `source_dir` | Directory containing source code files | Required |
| `output_dir` | Directory where translated files will be saved | Required |
| `--source-lang` | Source programming language | "java" |
| `--target-lang` | Target programming language | "javascript" |
| `--source-ext` | Source file extension | ".java" |
| `--target-ext` | Target file extension | ".js" |
| `--model` | OpenAI model to use | "gpt-4" |

## Example Code

The repository includes example code in the `examples` directory:

### Java to JavaScript Example

Source file (`examples/java_to_js/src/HelloWorld.java`):

```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }

    public static int add(int a, int b) {
        return a + b;
    }

    public static String greet(String name) {
        return "Hello, " + name + "!";
    }
}
```

## Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-code-eye.git
cd ai-code-eye

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
