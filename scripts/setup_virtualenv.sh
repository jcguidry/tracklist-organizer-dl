# Define the Python version and environment name
PYTHON_VERSION="python3.8"
ENV_NAME="py_venv"

# Create a new virtual environment
echo "Creating a virtual environment..."
virtualenv -p $PYTHON_VERSION $ENV_NAME

# Activate the virtual environment
echo "Activating the virtual environment..."
source $ENV_NAME/bin/activate

# Install the packages from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found."
fi

# Deactivate the virtual environment
echo "Setup complete."
# conda deactivate

# To make the script executable, run: chmod +x scripts/setup_virtualenv.sh
# Must run `pip install virtualenv`` on machine

# Then, to run the stup script, type: 
# scripts/setup_virtualenv.sh