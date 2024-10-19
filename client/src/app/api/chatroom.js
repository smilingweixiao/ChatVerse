import axios from 'axios';
// import 'babel-polyfill';
import moment from 'moment';

const baseURL = 'http://127.0.0.1:5000'

async function server_generate_chat(userInput) {
    
    const newMessage = {
        speaker: 0,
        message: userInput,
        timestamp: moment().format('YYYY-MM-DD HH:mm:ss')
    };
    
    return {speaker: 3, message: "hihihihi", timestamp: "2024-11-11 11:11:11"}
  
    let response = await axios.post(`${baseURL}/api/chat`, newMessage);
    console.log('agent say: ', response);
    return response.data;
}
  
export async function generate_chat(userInput) {
    try {
        const updatedMessages = await server_generate_chat(userInput);
        return updatedMessages;
    } catch (error) {
        console.error('Error updating hatHistory: ', error);
    }
  
}

async function server_start_recording() {
    
    return {speaker: 1, message: "start recording", timestamp: "2024-11-11 11:11:11"}
  
    let response = await axios.post(`${baseURL}/api/start_recording`);
    console.log('recording says: ', response);
    return response.data;
}
  
export async function start_recording() {

    try {
        const start_signal = await server_start_recording();
        return start_signal;
    } catch (error) {
        console.error('Error start recording: ', error);
    }
  
}


async function server_stop_recording() {
    
    return {speaker: 0, message: "finish recording", timestamp: "2024-22-22 22:22:22"}
  
    let response = await axios.post(`${baseURL}/api/stop_recording`);
    console.log('recording says: ', response);
    return response.data;
}
  
export async function stop_recording() {
    try {
        const updatedMessages = await server_stop_recording();
        return updatedMessages;
    } catch (error) {
        console.error('Error start recording: ', error);
    }
  
}