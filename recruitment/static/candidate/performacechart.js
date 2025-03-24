$(document).ready(function(){
    const mainData = [
        { name: "Education", value: 20, color: "#8B5CF6" },
        { name: "Experience", value: 15, color: "#60A5FA" },
        { name: "Skills", value: 25, color: "#10B981" },
        { name: "Achievements", value: 15, color: "#7C3AED" },
        { name: "Remaining Potential", value: 25, color: "#CBD5E1" },
    ];

    const skillsData = [
        { name: "Technical Skills", value: 40, color: "#8B5CF6" },
        { name: "Soft Skills", value: 20, color: "#1F2937" },
        { name: "Potential Development", value: 40, color: "#10B981" },
    ];

    const achievementsData = [
        { name: "Projects", value: 30, color: "#7C3AED" },
        { name: "Certifications", value: 15, color: "#10B981" },
        { name: "Awards", value: 5, color: "#F43F5E" },
        { name: "Professional Presence", value: 10, color: "#8B5CF6" },
        { name: "Remaining Potential", value: 40, color: "#CBD5E1" },
    ];

    function createDoughnutChart(elementId, data) {
        const ctx = document.getElementById(elementId).getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.map(item => item.name),
                datasets: [{
                    data: data.map(item => item.value),
                    backgroundColor: data.map(item => item.color),
                    borderWidth: 0,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false,
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.label}: ${context.parsed}%`;
                            }
                        }
                    }
                },
                cutout: '60%',
                animation: {
                    animateRotate: true,
                    animateScale: true
                }
            }
        });
    }

    function createLegend(elementId, data) {
        const legend = document.getElementById(elementId);
        data.forEach(item => {
            const div = document.createElement('div');
            div.className = 'flex items-center gap-2 bg-white/50 dark:bg-gray-800/50 px-3 py-1 rounded-full';
            div.innerHTML = `
                <div class="w-3 h-3 rounded-full" style="background-color: ${item.color}"></div>
                <span class="text-sm text-gray-600 dark:text-gray-400">${item.name}</span>
            `;
            legend.appendChild(div);
        });
    }

    createDoughnutChart('mainChart', mainData);
    createDoughnutChart('skillsChart', skillsData);
    createDoughnutChart('achievementsChart', achievementsData);

    createLegend('mainLegend', mainData);
    createLegend('skillsLegend', skillsData);
    createLegend('achievementsLegend', achievementsData);


    let resume_impact_chart;
    function candidateChart() {
        // Get canvas element
        const canvas = document.getElementById('resumeImpactChart');
        // Get values from data attributes
        const chartData = {
            labels: ['Education', 'Experience', 'Skills', 'Achievements', 'Remaining Potential'],
            values: [
                0.25 * parseFloat(canvas.dataset.education) || 0,
                0.30 * parseFloat(canvas.dataset.experience) || 0,
                0.30 * parseFloat(canvas.dataset.skills) || 0,
                0.15 * parseFloat(canvas.dataset.achievements) || 0,
                0 // Placeholder for remaining potential
            ]
        };
        // Calculate total of current values
        const currentTotal = chartData.values.slice(0, -1).reduce((a, b) => a + b, 0);

        // Calculate and set remaining potential
        chartData.values[4] = Math.max(0, 100 - currentTotal);

        const data = {
            labels: chartData.labels,
            datasets: [{
                data: chartData.values,
                backgroundColor: [
                    '#8b5cf6',   // Level 1 - Slate
                    '#60a5fa',   // Level 2 - Blue
                    '#22c55e',   // Level 3 - Green
                    '#6366f1',   // Level 4 - Indigo
                    '#94a3b8',    // Level 5 - Purple
                    ],
                borderWidth: 1,
                borderColor: '#fff'
            }]
        };

        const ctx = canvas.getContext('2d');

        if (resume_impact_chart) {
            resume_impact_chart.destroy();
        }

        resume_impact_chart = new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                return `${label}: ${value.toFixed(1)}%`;
                            }
                        }
                    }
                },
            }
        });
    }

    // Initialize the chart
    candidateChart();

    let experienceChart;

    function displayExperienceImpact() {
        const canvas = document.getElementById('experienceImpactChart');

        // Get experience impact value from data attribute (out of 100)
        const experienceImpact = parseFloat(canvas.dataset.experienceImpact) || 0;
        const maxScore = 100;
        const remainingPotential = Math.max(0, maxScore - experienceImpact);

        // Calculate years of experience (if provided)
        const yearsExperience = parseFloat(canvas.dataset.yearsExperience) || 0;

        const data = {
            labels: ['Experience Impact', 'Remaining Potential'],
            datasets: [{
                data: [experienceImpact, remainingPotential],
                backgroundColor: [
                    '#4A235A',  // Purple for experience impact
                    '#E0E0E0'   // Gray for remaining potential
                ],
                borderWidth: 1,
                borderColor: '#fff'
            }]
        };

        const ctx = canvas.getContext('2d');

        if (experienceChart) {
            experienceChart.destroy();
        }

        experienceChart = new Chart(ctx, {
            type: 'pie',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%', // Makes the doughnut chart thinner
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            font: {
                                size: 12
                            },
                            generateLabels: function(chart) {
                                const data = chart.data;
                                if (data.labels.length && data.datasets.length) {
                                    return data.labels.map((label, i) => ({
                                        text: `${label}: ${data.datasets[0].data[i].toFixed(1)}%`,
                                        fillStyle: data.datasets[0].backgroundColor[i],
                                        strokeStyle: data.datasets[0].borderColor,
                                        lineWidth: data.datasets[0].borderWidth,
                                        hidden: isNaN(data.datasets[0].data[i]) || data.datasets[0].data[i] === 0,
                                        index: i
                                    }));
                                }
                                return [];
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                let tooltipText = `${label}: ${value.toFixed(1)}%`;
                                if (label === 'Experience Impact' && yearsExperience > 0) {
                                    tooltipText += `\nYears of Experience: ${yearsExperience}`;
                                }
                                return tooltipText;
                            }
                        }
                    }
                },
                animation: {
                    animateScale: true,
                    animateRotate: true
                }
            }
        });

        // Add center text showing experience impact
        const originalDraw = experienceChart.draw;
        experienceChart.draw = function() {
            originalDraw.apply(this, arguments);

            const width = this.width;
            const height = this.height;
            const ctx = this.ctx;
            ctx.save();
        };
    }

    // Initialize the chart
    displayExperienceImpact();
    let educationLevelChart;

    function displayEducationLevel() {
        const canvas = document.getElementById('educationLevelChart');
        // Get education level from data attribute and parse it
        const currentEducationLevel = parseInt(canvas.dataset.educationLevel) || 0;
        const totalLevels = 4;

        const ctx = canvas.getContext('2d');

        if (educationLevelChart) {
            educationLevelChart.destroy();
        }

        educationLevelChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [''],
                datasets: [{
                    data: [totalLevels],
                    backgroundColor: function(context) {
                        const chart = context.chart;
                        const {ctx, chartArea} = chart;
                        if (!chartArea) return;

                        const gradient = ctx.createLinearGradient(
                            chartArea.left, 0,
                            chartArea.right, 0
                        );

                        const gapSize = 0.02;
                        const stepSize = 1 / totalLevels;

                        for (let i = 0; i < totalLevels; i++) {
                            const start = i * stepSize;
                            const end = start + stepSize - gapSize;

                            if (i < currentEducationLevel) {
                                gradient.addColorStop(start, '#22c55e');
                                gradient.addColorStop(end, '#22c55e');
                            } else {
                                gradient.addColorStop(start, '#E0E0E0');
                                gradient.addColorStop(end, '#E0E0E0');
                            }

                            const gapStart = end;
                            const gapEnd = start + stepSize;
                            gradient.addColorStop(gapStart, 'white');
                            gradient.addColorStop(gapEnd, 'white');
                        }

                        return gradient;
                    },
                    borderWidth: 0
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        display: true,
                        grid: {
                            display: false
                        },
                        ticks: {
                            stepSize: 1,
                            color: 'black',
                            callback: function(value) {
                                return value >= 0 && value <= 4 ? '' : '';
                            }
                        },
                        min: 0,
                        max: totalLevels
                    },
                    y: {
                        display: false
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Current Level: ${currentEducationLevel} / ${totalLevels}`;
                            }
                        }
                    },
                    afterDraw: (chart) => {
                        const ctx = chart.ctx;
                        const chartArea = chart.chartArea;
                        const xAxis = chart.scales.x;

                        // Calculate position for the arrow
                        const arrowX = xAxis.getPixelForValue(currentEducationLevel);
                        const arrowY = chartArea.bottom + 1;

                        // Draw arrow
                        ctx.save();
                        ctx.beginPath();
                        ctx.moveTo(arrowX, arrowY);
                        ctx.lineTo(arrowX - 10, arrowY + 15);
                        ctx.lineTo(arrowX + 10, arrowY + 15);
                        ctx.closePath();
                        ctx.fillStyle = '#4A235A';
                        ctx.fill();
                        ctx.restore();
                    }
                },
                barThickness: 20
            }
        });
    }

    // Initialize the chart
    displayEducationLevel();


    let skillsChart;

    function displaySkillsBreakdown() {
        // Get canvas element
        const canvas = document.getElementById('skillsBreakdownChart');

        // Get values from data attributes
        const technicalSkills = parseFloat(canvas.dataset.technicalSkills) || 0;
        const softSkills = parseFloat(canvas.dataset.softSkills) || 0;

        // Calculate remaining potential
        const maxScore = 100;
        const remainingPotential = Math.max(0, maxScore - (technicalSkills + softSkills));

        const data = {
            labels: ['Technical Skills', 'Soft Skills', 'Remaining Potential'],
            datasets: [{
                data: [technicalSkills, softSkills, remainingPotential],
                backgroundColor: [
                    '#22c55e',   // Level 3 - Green
                    '#6366f1',   // Level 4 - Indigo
                    '#E0E0E0'   // Gray for remaining potential (matching education chart)
                ],
                borderWidth: 1,
                borderColor: '#fff'
            }]
        };

        const ctx = canvas.getContext('2d');

        if (skillsChart) {
            skillsChart.destroy();
        }

        skillsChart = new Chart(ctx, {
            type: 'pie',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            font: {
                                size: 12
                            },
                            generateLabels: function(chart) {
                                const data = chart.data;
                                if (data.labels.length && data.datasets.length) {
                                    return data.labels.map((label, i) => ({
                                        text: `${label}: ${data.datasets[0].data[i].toFixed(1)}%`,
                                        fillStyle: data.datasets[0].backgroundColor[i],
                                        strokeStyle: data.datasets[0].borderColor,
                                        lineWidth: data.datasets[0].borderWidth,
                                        hidden: isNaN(data.datasets[0].data[i]) || data.datasets[0].data[i] === 0,
                                        index: i
                                    }));
                                }
                                return [];
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                return `${label}: ${value.toFixed(1)}%`;
                            }
                        }
                    }
                }
            }
        });
    }

    // Initialize the chart
    displaySkillsBreakdown();


    let achievementsChart;

    function displayAchievementsBreakdown() {
        const canvas = document.getElementById('achievementsChart');

        // Get values from data attributes (out of 100 for each category)
        const awards = parseFloat(canvas.dataset.awards) || 0;
        const projects = parseFloat(canvas.dataset.projects) || 0;
        const professionalPresence = parseFloat(canvas.dataset.professionalPresence) || 0;

        // Calculate total achievement score and remaining potential
        const maxScore = 100;
        const totalScore = (awards + projects + professionalPresence) / 3; // Average of all scores
        const remainingPotential = Math.max(0, maxScore - totalScore);

        const data = {
            labels: ['Awards', 'Projects', 'Professional Presence', 'Remaining Potential'],
            datasets: [{
                data: [awards, projects, professionalPresence, remainingPotential],
                backgroundColor: [
                    '#8b5cf6',   // Level 1 - Slate
                    '#60a5fa',   // Level 2 - Blue
                    '#22c55e',   // Level 3 - Green
                    '#E0E0E0'   // Gray for remaining potential
                ],
                borderWidth: 1,
                borderColor: '#fff'
            }]
        };

        const ctx = canvas.getContext('2d');

        if (achievementsChart) {
            achievementsChart.destroy();
        }

        achievementsChart = new Chart(ctx, {
            type: 'doughnut', // Using doughnut chart for better visualization
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%', // Makes the doughnut chart thinner
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            font: {
                                size: 12
                            },
                            generateLabels: function(chart) {
                                const data = chart.data;
                                if (data.labels.length && data.datasets.length) {
                                    return data.labels.map((label, i) => ({
                                        text: `${label}: ${data.datasets[0].data[i].toFixed(1)}%`,
                                        fillStyle: data.datasets[0].backgroundColor[i],
                                        strokeStyle: data.datasets[0].borderColor,
                                        lineWidth: data.datasets[0].borderWidth,
                                        hidden: isNaN(data.datasets[0].data[i]) || data.datasets[0].data[i] === 0,
                                        index: i
                                    }));
                                }
                                return [];
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                return `${label}: ${value.toFixed(1)}%`;
                            },
                        }
                    }
                },
                animation: {
                    animateScale: true,
                    animateRotate: true
                }
            }
        });

        // Add center text with total score
        const originalDraw = achievementsChart.draw;
        achievementsChart.draw = function() {
            originalDraw.apply(this, arguments);
            const width = this.width;
            const height = this.height;
            const ctx = this.ctx;

            ctx.restore();
            ctx.font = "bold 16px Arial";
            ctx.textBaseline = 'middle';
            ctx.textAlign = 'center';
            ctx.fillStyle = '#4A235A';
            ctx.font = "12px Arial";
            ctx.save();
        };
    }

    // Initialize the chart
    displayAchievementsBreakdown();



});