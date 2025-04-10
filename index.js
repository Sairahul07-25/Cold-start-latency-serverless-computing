
const window_size = 24; 
const threshold = 0.6;  
const warm_up_time = 0.1; 

let invocationHistory = [];

function getInvocationFrequency() {
    const now = new Date();
    const recentInvocations = invocationHistory.filter(invocation => {
        const timeDiff = (now - new Date(invocation.timestamp)) / (1000 * 60 * 60); 
        return timeDiff <= window_size;
    });
    return recentInvocations.length / window_size; 
}

function predictionAnalysis() {
    const frequency = getInvocationFrequency();
    console.log("Recent Invocation Frequency: ", frequency);

    const probability = frequency >= 0.5 ? 0.8 : 0.4; 
    console.log("Predicted Confidence: ", probability);

    return probability;
}

function coldStart() {
    console.log("Starting a cold start...");
    return new Promise(resolve => setTimeout(resolve, warm_up_time * 1000));
}

exports.handler = async (event) => {
    const now = new Date();
    invocationHistory.push({ timestamp: now });

    const predictedConfidence = predictionAnalysis();

    let response;

    if (predictedConfidence >= threshold) {
        console.log("Using existing container...");
        response = {
            statusCode: 200,
            body: JSON.stringify({ message: "Used pre-warmed container" }),
        };
    } else {
        console.log("Cold start path triggered...");
        await coldStart();
        response = {
            statusCode: 200,
            body: JSON.stringify({ message: "Cold start completed" }),
        };
    }

    return response;
};
