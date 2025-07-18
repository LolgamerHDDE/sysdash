﻿# SysDash - A System Dashboard

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

SysDash is a comprehensive web-based system monitoring and performance testing dashboard built with FastAPI and Bootstrap. It provides real-time system information, performance benchmarks, and network speed testing capabilities through an intuitive web interface.

![SysDash Screenshot](screenshot.png)

## 🚀 Features

### 📊 System Monitoring
- **CPU Information**: Real-time CPU usage, core count, frequency, and detailed processor information
- **Memory Monitoring**: RAM usage, available memory, and memory statistics
- **Disk Management**: Disk partitions, usage statistics, and I/O performance metrics
- **Network Statistics**: Network interfaces, traffic statistics, and connection information

### ⚡ Performance Benchmarking
- **CPU Benchmarks**: Single-threaded and multi-threaded performance tests
- **RAM Speed Tests**: Memory copy speed and throughput measurements
- **Disk I/O Tests**: Read/write speed benchmarks for storage devices
- **GPU Performance**: CUDA-based GPU performance testing (NVIDIA GPUs only)

### 🌐 Network Speed Testing
- **Ping Tests**: Latency measurements to test servers
- **Download Speed**: Internet download speed testing
- **Upload Speed**: Internet upload speed testing
- **Comprehensive Results**: Detailed network performance metrics

### 🎨 Modern Web Interface
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Real-time Updates**: Live system information updates
- **Interactive Charts**: Visual representation of system metrics
- **Bootstrap UI**: Clean, professional interface design

## 📋 Requirements

### System Requirements
- Python 3.8 or higher
- Windows, macOS, or Linux
- For GPU benchmarking: NVIDIA GPU with CUDA support (optional)

### Python Dependencies
```
fastapi>=0.68.0
uvicorn[standard]>=0.15.0
jinja2>=3.0.0
python-multipart>=0.0.5
requests>=2.25.0
psutil>=5.8.0
numpy>=1.21.0
numba>=0.56.0
```

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/LolgamerHDDE/sysdash.git
cd sysdash
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python main.py
```

The application will be available at `http://127.0.0.1:8000`

## 📁 Project Structure

```
sysdash/
├── LICENSE                 # MIT License
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── backend/               # Backend modules
│   ├── __init__.py
│   ├── sysinfo.py         # System information collection
│   ├── benchmark.py       # Performance benchmarking
│   └── speedtest.py       # Network speed testing
├── frontend/              # HTML templates
│   ├── index.html         # Dashboard homepage
│   ├── components.html    # System information page
│   └── tests.html         # Performance testing page
└── static/                # Static assets
    └── style.css          # Custom CSS styles
```

## 🔧 Configuration

### Environment Variables
You can configure the application using environment variables:

```bash
# Server configuration
HOST=127.0.0.1
PORT=8000

# Speedtest server (optional)
SPEEDTEST_SERVER_URL=http://fra1.syncwi.de:8080
```

### Custom Speedtest Server
To use a custom speedtest server, modify the `SERVER_URL` in `backend/speedtest.py`:

```python
SERVER_URL = "http://your-speedtest-server.com:8080"
```

## 🚀 Usage

### Web Interface

1. **Overview Page** (`/`): Dashboard homepage with system overview and quick stats
2. **Components Page** (`/components`): Detailed system information and real-time monitoring
3. **Tests Page** (`/tests`): Performance benchmarking and speed testing interface

### API Endpoints

#### System Information
- `GET /api/components` - Complete system information
- `GET /api/cpu` - CPU information and usage
- `GET /api/ram` - Memory information and usage
- `GET /api/disk` - Disk partitions and I/O statistics
- `GET /api/network` - Network interfaces and statistics

#### Performance Benchmarks
- `GET /api/benchmark` - Run complete benchmark suite
- `GET /api/benchmark/cpu-single` - Single-threaded CPU benchmark
- `GET /api/benchmark/cpu-multi` - Multi-threaded CPU benchmark
- `GET /api/benchmark/ram` - RAM speed benchmark
- `GET /api/benchmark/disk` - Disk I/O benchmark
- `GET /api/benchmark/gpu` - GPU performance benchmark

#### Network Speed Tests
- `GET /api/speedtest` - Complete speed test
- `GET /api/speedtest/ping` - Ping test only
- `GET /api/speedtest/download` - Download speed test
- `GET /api/speedtest/upload` - Upload speed test

### Example API Usage

```bash
# Get system information
curl http://127.0.0.1:8000/api/components

# Run CPU benchmark
curl http://127.0.0.1:8000/api/benchmark/cpu-single

# Test network speed
curl http://127.0.0.1:8000/api/speedtest/ping
```

> **SECURITY NOTICE**: Please make sure that Port 8000/tcp is not open via your Router!

## 🔍 Troubleshooting

### Common Issues

#### Backend Functions Not Available
```
Warning: Could not import backend functions
```
**Solution**: Install required dependencies:
```bash
pip install psutil numpy numba
```

#### GPU Benchmark Returns "N/A"
This is normal if you don't have an NVIDIA GPU with CUDA support. GPU benchmarking requires:
- NVIDIA GPU
- CUDA drivers installed
- CUDA toolkit
- Numba with CUDA support: `pip install numba[cuda]`

#### Multiprocessing Errors on Windows
```
Can't get local object 'cpu_multi_thread.<locals>.worker'
```
**Solution**: This is fixed in the current version. Make sure you're using the latest code.

#### Speedtest Server Unreachable
If the default speedtest server is unavailable, you can:
1. Use a different server by modifying `SERVER_URL` in `backend/speedtest.py`
2. Set up your own speedtest server
3. The application will still work without speedtest functionality

### Performance Considerations

- **Benchmarks**: Performance tests are CPU/disk intensive and may take several seconds to complete
- **Memory Usage**: RAM benchmarks use significant memory (500MB+)
- **Network Tests**: Speed tests consume bandwidth and may take 30-60 seconds

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Run tests (if available)
5. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
6. Push to the branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and small

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework for building APIs
- [Bootstrap](https://getbootstrap.com/) - CSS framework for responsive design
- [psutil](https://github.com/giampaolo/psutil) - Cross-platform system and process utilities
- [NumPy](https://numpy.org/) - Numerical computing library
- [Numba](https://numba.pydata.org/) - JIT compiler for Python

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Search existing [Issues](https://github.com/LolgamerHDDE/sysdash/issues)
3. Create a new issue with detailed information about your problem

## 🔄 Changelog

### v1.0.0 (Current)
- Initial release
- System monitoring dashboard
- Performance benchmarking suite
- Network speed testing
- Responsive web interface
- REST API endpoints

---

**Made with ❤️ by [LolgamerHD](https://github.com/LolgamerHDDE)**
