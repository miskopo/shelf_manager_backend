from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import shutil
import sys

with open("requirements.txt") as req_file:
    REQUIREMENTS: list = req_file.readlines()

with open("README.md") as readme_file:
    LONG_DESC: str = "\n".join(readme_file.readlines())

class InstallWithService(install):
    """Custom installation command that also installs systemd service file."""
    def run(self):
        install.run(self)  # Perform standard installation first

        # Install systemd service
        service_src = os.path.join(os.path.dirname(__file__), 'systemd', 'pantry-scanner.service')
        service_dst = '/etc/systemd/system/pantry-scanner.service'

        if os.geteuid() != 0:
            print("⚠️  You need to run installation as root to install the systemd service.")
            print(f"Skipping systemd service installation: {service_dst}")
            return

        try:
            shutil.copy(service_src, service_dst)
            print(f"✅ Installed systemd service to {service_dst}")
            os.system('systemctl daemon-reload')
            os.system('systemctl enable pantry-scanner.service')
            print("✅ Systemd service enabled.")
        except Exception as e:
            print(f"❌ Failed to install systemd service: {e}")
            sys.exit(1)


setup(
    name="pantry-scanner",
    version="0.1.0",
    author="miskopo",
    description="Barcode management and scanner integration for homemade preserves.",
    long_description=LONG_DESC,
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=REQUIREMENTS,
    entry_points={
        "console_scripts": [
            "pantry-scanner = pantry.service:main",
        ],
    },
    cmdclass={
        'install': InstallWithService,
    },
    include_package_data=True,
)