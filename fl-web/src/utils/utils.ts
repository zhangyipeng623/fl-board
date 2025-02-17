import { state } from "@/utils/settings";
import axios from "axios";

const center = axios.create({
    baseURL: "http://" + state.center.ip + ":" + state.center.port,
});
center.interceptors.request.use((config) => {
    config.headers['session'] = localStorage.getItem("userSession");
    return config;
}, (error) => {
    return Promise.reject(error);
});

const user = axios.create({
    baseURL: "http://" + state.user.ip + ":" + state.user.port,
});

user.interceptors.request.use((config) => {
    config.headers['session'] = localStorage.getItem("userSession");
    return config;
}, (error) => {
    return Promise.reject(error);
});

export {center,user};

export const getNodeStatus = async () => {
    try{
        const res = await center.get("/node/status");
        state.updateDbNode(res.data.user_list);
        state.updateCenterInfo(true);
        console.log(res.data);
    }catch(e){
        console.log(e);
    }
};