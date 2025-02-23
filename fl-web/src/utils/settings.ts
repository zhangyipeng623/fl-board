import { reactive} from "vue";

export interface DbNode {
    id: number;
    name: string;
    ip: string;
    port: string;
    is_connect: boolean;
}

export const state = reactive({
    
    user:{
        id: 0,
        name: "本地节点",
        ip: "127.0.0.1",
        port: "8100",
        is_connect: false,
    } as DbNode,
    center:{
        id:0,
        name:"center",
        ip:"127.0.0.1",
        port:"8000",
        is_connect:false,
    } as DbNode,

    updateUserInfo: (id: number, username: string, ip: string, port: string, isLogin: boolean) => {
        state.user.id = id;
        state.user.name = username;
        state.user.ip = ip;
        state.user.port = port;
        state.user.is_connect = isLogin;
        
    },
    updateCenterInfo: (is_connect: boolean) => {
        state.center.is_connect = is_connect
    },
})

