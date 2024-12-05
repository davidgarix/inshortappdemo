#!/bin/zsh

# Function to handle errors and exit if any command fails
handle_error() {
  echo "❌ Error: $1"
  exit 1
}

# Step 1: Check if Homebrew is installed, and install if not
echo "🔧 Checking if Homebrew is installed..."
if ! command -v brew &> /dev/null; then
  echo "❌ Homebrew is not installed. Attempting to install Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  if [ $? -ne 0 ]; then
    handle_error "Failed to install Homebrew."
  fi
else
  echo "✅ Homebrew is installed."
fi

# Step 2: Activate the Python virtual environment
echo "🔧 Checking for the virtual environment..."
CURRENT_DIR=$(pwd)
if [ ! -d "venv" ]; then
  echo "❌ Virtual environment not found. Do you want to create one? (y/n)"
  read answer
  if [ "$answer" != "${answer#[Yy]}" ]; then
    python3 -m venv venv
    source venv/bin/activate
  else
    handle_error "Virtual environment not found and not created."
  fi
else
  source $CURRENT_DIR/venv/bin/activate
  if [ $? -ne 0 ]; then
    handle_error "Failed to activate the virtual environment. Make sure it is created."
  fi
fi
echo "✅ Virtual environment activated."

# Step 3: Install required packages
echo "🔧 Installing required packages..."

# Update pip to latest version first
echo "📦 Updating pip to latest version..."
if ! python -m pip install --upgrade pip; then
  handle_error "Failed to update pip"
fi
echo "✅ pip updated successfully"

# Define packages with versions
PACKAGES=(
  "python-dotenv"
  "Flask"
  "Jinja2"
  "lxml"
  "MarkupSafe"
  "requests"
  "urllib3"
  "Werkzeug"
  "gunicorn"
  "flask-cors"
  "pytz"
)

# Function to check if package is installed
check_package() {
  pip show $1 &> /dev/null
  return $?
}

# Install packages
for package in "${PACKAGES[@]}"; do
  package_name=$(echo "$package" | cut -d '>' -f1)
  echo "📦 Installing latest $package..."
  
  # Install/upgrade to latest version using --upgrade flag
  if ! pip install --upgrade "$package"; then
    handle_error "Failed to install package: $package"
  fi
  echo "✅ Successfully installed $package"
done

# Verify installations
echo "🔍 Verifying package installations..."
for package in "${PACKAGES[@]}"; do
  package_name=$(echo "$package" | cut -d '>' -f1)
  if ! check_package "$package_name"; then
    handle_error "Package $package_name was not installed correctly."
  fi
done
echo "✅ All packages verified successfully."

# Final success message
echo "🎉 All dependencies installed successfully!"

# Create requirements.txt file
echo "📝 Creating requirements.txt file..."
if ! pip freeze > requirements.txt; then
  handle_error "Failed to create requirements.txt file."
fi
echo "✅ requirements.txt file created successfully."

echo "🚀 You can now proceed with your project."

