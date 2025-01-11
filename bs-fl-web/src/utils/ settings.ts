import { reactive } from "vue";

export const state = reactive({
    
    user:{
        username: "",
        token: "",
        isLogin: false,
    },
    center:{
        ip_port: "",
        is_connect: false,
    },

    local_ip_port: "127.0.0.1:8000",

    updateUserInfo: (username: string, token: string, isLogin: boolean) => {
        state.user.username = username;
        state.user.token = token;
        state.user.isLogin = isLogin;
    },
    updateCenterInfo: (ip_port: string, is_connect: boolean) => {
        state.center.ip_port = ip_port;
        state.center.is_connect = is_connect;
    }
})


