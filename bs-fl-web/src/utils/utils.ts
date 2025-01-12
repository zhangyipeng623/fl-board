import { state } from "@/utils/settings";
import axios from "axios";
export const getNodeStatus = async () => {
    try{
        const res = await axios.get("http://" + state.center.ip + ":" + state.center.port + "/node/status");
        state.updateDbNode(res.data.user_list);
        state.updateCenterInfo(true);
        console.log(res.data);
    }catch(e){
        console.log(e);
    }
};