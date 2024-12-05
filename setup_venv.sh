#!/bin/zsh

# Function to handle errors and exit if any command fails
handle_error() {
  echo "❌ Error: $1"
  exit 1
}

# Step 1: Install direnv using Homebrew
echo "🔧 Installing direnv..."
if ! brew install direnv; then
  handle_error "Failed to install direnv. Please check your Homebrew installation."
fi
echo "✅ direnv installed successfully."

# Step 2: Add direnv hook to Zsh configuration
echo "🔧 Adding direnv hook to Zsh..."
if ! eval "$(direnv hook zsh)"; then
  handle_error "Failed to add direnv hook to Zsh."
fi
echo "✅ direnv hook added to Zsh."

# Step 3: Reload Zsh configuration
echo "🔧 Reloading Zsh configuration..."
if ! source ~/.zshrc; then
  handle_error "Failed to reload Zsh configuration."
fi
echo "✅ Zsh configuration reloaded."

# Step 4: Get the current working directory
CURRENT_DIR=$(pwd)
echo "📂 Current directory is: $CURRENT_DIR"

# Step 5: Create a Python virtual environment in the current directory
echo "🔧 Creating a virtual environment in $CURRENT_DIR..."
if ! python3 -m venv venv; then
  handle_error "Failed to create virtual environment. Make sure Python3 is installed."
fi
echo "✅ Virtual environment created."

# Step 6: Write the virtual environment activation command to .envrc
echo "🔧 Setting up .envrc file..."
if ! echo "source $CURRENT_DIR/venv/bin/activate" > .envrc; then
  handle_error "Failed to write to .envrc."
fi
echo "✅ .envrc file set up."

# Step 7: Allow direnv to use the .envrc file
echo "🔧 Allowing direnv to load the .envrc file..."
if ! direnv allow; then
  handle_error "Failed to allow direnv to load the .envrc file."
fi
echo "✅ direnv allowed to load the .envrc file."

# Step 8: Final success message and prompt to close the terminal
echo "🎉 Virtual environment created and direnv configured successfully!"
echo "🚀 You can now close the terminal or continue working in the virtual environment."

