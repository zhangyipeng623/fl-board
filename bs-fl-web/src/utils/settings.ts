import { reactive, ref } from "vue";

export interface DbNode {
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
    },
    center:{
        name:"中心节点",
        ip:"127.0.0.1",
        port:"8000",
        is_connect:false,
    } as DbNode,
    db_node:ref([] as DbNode[]),

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
    updateDbNode: (db_node: DbNode[]) => {
        state.db_node = db_node;
    }
})

