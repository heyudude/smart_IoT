$(function() {
    class GaugeChart {
        constructor(element, params) {
            this._element = element;
            this._initialValue = params.initialValue;
            this._higherValue = params.higherValue;
            this._title = params.title;
            this._subtitle = params.subtitle;
        }

        _buildConfig() {
            let element = this._element;

            return {
                value: this._initialValue,
                valueIndicator: {
                    color: '#fff'
                },
                geometry: {
                    startAngle: 180,
                    endAngle: 360
                },
                scale: {
                    startValue: 0,
                    endValue: this._higherValue,
                    customTicks: [0, 20, 40, 60, 80, 100, 120],
                    tick: { 
                        length: 8
                    },
                    label: {
                        font: {
                            color: '#87959f',
                            size: 9,
                            family: '"Open Sans", sans-serif'
                        }
                    }
                },
                title: {
                    verticalAlignment: 'bottom',
                    text: this._title,
                    font: {
                        family: '"Open Sans", sans-serif',
                        color: '#fff',
                        size: 10
                    },
                    subtitle: {
                        text: this._subtitle,
                        font: {
                            family: '"Open Sans", sans-serif',
                            color: '#fff',
                            weight: 700,
                            size: 15
                        }
                    }
                }
            };
        }

        init() {
            $(this._element).dxCircularGauge(this._buildConfig());
        }
    }

    // Initialize the gauges with placeholder data
    const gauges = [
        { element: '#temperature-gauge', initialValue: 0, higherValue: 50, title: 'Temperature', subtitle: '0 ºC' },
        { element: '#humidity-gauge', initialValue: 0, higherValue: 100, title: 'Humidity', subtitle: '0 %' },
        { element: '#ammonia-gauge', initialValue: 0, higherValue: 120, title: 'Gas Sensor', subtitle: '0 ppm' }
    ];

    gauges.forEach((gaugeData) => {
        let gauge = new GaugeChart(gaugeData.element, gaugeData);
        gauge.init();
    });

    // Function to update the gauge values
    function updateGauges(sensorData) {
        const latestData = sensorData.sensor_data.slice(-1)[0];  // Get the latest sensor data
        
        // Update the temperature gauge
        const temperatureGauge = $("#temperature-gauge").dxCircularGauge('instance');
        temperatureGauge.value(latestData.temperature);
        const tempText = $("#temperature-gauge").find('.dxg-title text').last();
        tempText.html(`${latestData.temperature} ºC`);
        tempText.css("font-size", "20px");  
        tempText.css("margin-left", "10px");  
    
        // Update the humidity gauge
        const humidityGauge = $("#humidity-gauge").dxCircularGauge('instance');
        humidityValue = latestData.humidity.toFixed(1);
        humidityGauge.value(humidityValue);
        const humidityText = $("#humidity-gauge").find('.dxg-title text').last();
        humidityText.html(`${latestData.humidity} %`);
        humidityText.css("font-size", "20px"); 
        humidityText.css("margin-left", "10px");  
    
        // Update the gas sensor gauge
        const gasGauge = $("#ammonia-gauge").dxCircularGauge('instance');
        gasGauge.value(latestData.gas_sensor);
        const gasText = $("#ammonia-gauge").find('.dxg-title text').last();
        gasText.html(`${(latestData.gas_sensor)}ppm`);
        gasText.css("font-size", "20px");  
        gasText.css("margin-left", "10px");  
    }    

    // Function to fetch data from the backend
    function fetchData() {
        $.ajax({
            url: 'http://127.0.0.1:8000/api/devices/',
            method: 'GET',
            success: function(response) {
                if (response.length > 0) {
                    updateGauges(response[0]);  // Assuming you're using the first device
                }
            },
            error: function(xhr, status, error) {
                console.error("Error fetching data:", error);
            }
        });
    }

    // Fetch data every 10 seconds
    setInterval(fetchData, 10000);  // 10000 ms = 10 seconds

    // Initial data fetch
    fetchData();
});