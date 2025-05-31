// Pi Logarithmic Graph Visualization
class PiLogGraph {
    constructor() {
        // First 100 decimals of Pi
        this.piDecimals = "1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679";
        
        // Viridis colormap approximation for digits 0-9
        this.colors = [
            '#440154', // 0
            '#481668', // 1
            '#472d7b', // 2
            '#3e4989', // 3
            '#31688e', // 4
            '#26828e', // 5
            '#1f9e89', // 6
            '#35b779', // 7
            '#6ece58', // 8
            '#b5de2b'  // 9
        ];
        
        this.chart = null;
        this.currentRange = 100;
        
        this.init();
    }
    
    init() {
        this.displayPiDecimals();
        this.calculateStatistics();
        this.createChart();
        this.setupControls();
    }
    
    displayPiDecimals() {
        const decimalsElement = document.getElementById('pi-decimals');
        if (decimalsElement) {
            decimalsElement.textContent = this.piDecimals;
        }
    }
    
    calculateStatistics() {
        const stats = {};
        for (let i = 0; i <= 9; i++) {
            stats[i] = 0;
        }
        
        // Count occurrences of each digit
        for (let i = 0; i < this.piDecimals.length; i++) {
            const digit = parseInt(this.piDecimals[i]);
            stats[digit]++;
        }
        
        // Display statistics
        const statsGrid = document.getElementById('stats-grid');
        if (statsGrid) {
            statsGrid.innerHTML = '';
            
            for (let digit = 0; digit <= 9; digit++) {
                const count = stats[digit];
                const percentage = ((count / this.piDecimals.length) * 100).toFixed(1);
                
                const statItem = document.createElement('div');
                statItem.className = 'stat-item';
                statItem.style.borderTop = `3px solid ${this.colors[digit]}`;
                
                statItem.innerHTML = `
                    <div class="stat-digit">${digit}</div>
                    <div class="stat-count">${count} times</div>
                    <div class="stat-percentage">${percentage}%</div>
                `;
                
                statsGrid.appendChild(statItem);
            }
        }
    }
    
    calculateLogValues(range = 100) {
        const data = [];
        const labels = [];
        const backgroundColors = [];
        
        for (let i = 0; i < Math.min(range, this.piDecimals.length); i++) {
            const digit = parseInt(this.piDecimals[i]);
            const logValue = Math.log10(digit + 1); // Add 1 to avoid log(0)
            
            data.push(logValue);
            labels.push((i + 1).toString());
            backgroundColors.push(this.colors[digit]);
        }
        
        return { data, labels, backgroundColors };
    }
    
    createChart() {
        const ctx = document.getElementById('piChart');
        if (!ctx) return;
        
        const { data, labels, backgroundColors } = this.calculateLogValues(this.currentRange);
        
        this.chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'log₁₀(digit + 1)',
                    data: data,
                    backgroundColor: backgroundColors,
                    borderColor: backgroundColors.map(color => color + '80'),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Logarithmic Values of Pi\'s Decimal Digits',
                        font: {
                            size: 16,
                            weight: 'bold'
                        },
                        color: '#2c3e50'
                    },
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(44, 62, 80, 0.9)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: '#3498db',
                        borderWidth: 1,
                        callbacks: {
                            title: function(context) {
                                return `Position: ${context[0].label}`;
                            },
                            label: function(context) {
                                const position = parseInt(context.label) - 1;
                                const digit = parseInt(this.piDecimals[position]);
                                const logValue = context.parsed.y.toFixed(3);
                                return [
                                    `Digit: ${digit}`,
                                    `log₁₀(${digit} + 1) = ${logValue}`
                                ];
                            }.bind(this)
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Position in Pi\'s Decimal Sequence',
                            font: {
                                size: 14,
                                weight: 'bold'
                            },
                            color: '#2c3e50'
                        },
                        ticks: {
                            color: '#7f8c8d',
                            maxTicksLimit: 20
                        },
                        grid: {
                            color: 'rgba(127, 140, 141, 0.2)'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'log₁₀(digit + 1)',
                            font: {
                                size: 14,
                                weight: 'bold'
                            },
                            color: '#2c3e50'
                        },
                        ticks: {
                            color: '#7f8c8d'
                        },
                        grid: {
                            color: 'rgba(127, 140, 141, 0.2)'
                        },
                        min: 0,
                        max: 1.1
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }
    
    updateChart(range) {
        if (!this.chart) return;
        
        const { data, labels, backgroundColors } = this.calculateLogValues(range);
        
        this.chart.data.labels = labels;
        this.chart.data.datasets[0].data = data;
        this.chart.data.datasets[0].backgroundColor = backgroundColors;
        this.chart.data.datasets[0].borderColor = backgroundColors.map(color => color + '80');
        
        this.chart.update('active');
    }
    
    setupControls() {
        const rangeSlider = document.getElementById('rangeSlider');
        const rangeValue = document.getElementById('rangeValue');
        
        if (rangeSlider && rangeValue) {
            rangeSlider.addEventListener('input', (e) => {
                const newRange = parseInt(e.target.value);
                this.currentRange = newRange;
                rangeValue.textContent = newRange;
                this.updateChart(newRange);
            });
            
            // Initialize display
            rangeValue.textContent = this.currentRange;
        }
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PiLogGraph();
});

// Add some interactive enhancements
document.addEventListener('DOMContentLoaded', () => {
    // Add hover effects to stat items
    const statItems = document.querySelectorAll('.stat-item');
    statItems.forEach(item => {
        item.addEventListener('mouseenter', () => {
            item.style.transform = 'translateY(-2px) scale(1.02)';
            item.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.2)';
        });
        
        item.addEventListener('mouseleave', () => {
            item.style.transform = 'translateY(0) scale(1)';
            item.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)';
        });
    });
    
    // Add smooth scrolling for better UX
    document.documentElement.style.scrollBehavior = 'smooth';
    
    // Add loading animation completion
    setTimeout(() => {
        document.body.style.opacity = '1';
        document.body.style.transform = 'translateY(0)';
    }, 100);
});

// Add initial loading styles
document.addEventListener('DOMContentLoaded', () => {
    document.body.style.opacity = '0';
    document.body.style.transform = 'translateY(20px)';
    document.body.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
});