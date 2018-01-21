$(document).ready(function(){
    Highcharts.chart('highCharts', {
        chart: {
            backgroundColor: '#F4F4F4',
            zoomType: 'x'
        },
        title: {
            text: 'What do people think?'
        },
        subtitle: {
            text: document.ontouchstart === undefined ?
                    'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
        },
        xAxis: {
            type: 'datetime'
        },
        yAxis: {

            title: {
                text: 'Polarity'
            }
        },
        legend: {
            enabled: false
        },
        plotOptions: {
            area: {
                fillColor: {
                    linearGradient: {
                        x1: 0,
                        y1: 0,
                        x2: 0,
                        y2: 1
                    },
                    stops: [
                        [0, '#8ef9ff'],
                        [1, '#ffa5a5']
                    ]
                },
                marker: {
                    radius: 2
                },
                lineWidth: 1,
                states: {
                    hover: {
                        lineWidth: 1
                    }
                },
                threshold: null
            }
        },

        series: [{
            type: 'area',
            color: '#a5f9ff',
            name: 'Polarity',
            data: []
        }]
    });
});
