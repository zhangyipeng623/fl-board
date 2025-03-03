import { state } from "@/utils/settings";
import axios from "axios";

const center = axios.create({
    baseURL: "http://" + state.center.ip + ":" + state.center.port,
});
center.interceptors.request.use(
    (config) => {
        config.headers["Authorization"] = localStorage.getItem("userSession");
        config.headers["Access-Control-Expose-Headers"] = "session,authorization";
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

const user = axios.create({
    baseURL: "http://" + state.user.ip + ":" + state.user.port,
});

user.interceptors.request.use(
    (config) => {
        config.headers["Authorization"] = localStorage.getItem("userSession");
        config.headers["Access-Control-Expose-Headers"] = "session,authorization"
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export { center, user };
