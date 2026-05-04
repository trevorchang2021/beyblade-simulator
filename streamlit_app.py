import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="BX-10 3D 剛體對戰", layout="wide")

st.title("🌪️ BX-10 3D 立體剛體與極限加速模擬器")
st.markdown("突破沙盒限制！引入戰刃 3D 幾何結構、發射傾角，以及真實的軌道切線加速 (X-Dash) 物理演算。")

# --- 側邊欄控制項 ---
st.sidebar.header("🔵 UX-15 SharkScale (粉藍)")
ux_rpm = st.sidebar.slider("UX-15 抽力 (RPM)", 8000, 12000, 10000, step=100)
ux_angle_str = st.sidebar.radio("UX-15 發射角度", ["平 Shoot", "微斜 Shoot", "極限斜 Shoot"], key="ux_a")

st.sidebar.header("🟣 CX-01 Unicorn Sting (粉紫)")
cx_rpm = st.sidebar.slider("CX-01 抽力 (RPM)", 8000, 12000, 10000, step=100)
cx_angle_str = st.sidebar.radio("CX-01 發射角度", ["平 Shoot", "微斜 Shoot", "極限斜 Shoot"], key="cx_a")

# 角度轉換 (轉為弧度)
angle_map = {"平 Shoot": 0.0, "微斜 Shoot": 0.25, "極限斜 Shoot": 0.5}
ux_angle = angle_map[ux_angle_str]
cx_angle = angle_map[cx_angle_str]

if st.button("🚀 GO SHOOT! (啟動 3D 引擎)"):
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { margin: 0; overflow: hidden; background-color: #111; color: white; font-family: sans-serif; }
            #info { position: absolute; top: 10px; left: 10px; pointer-events: none; text-shadow: 1px 1px 2px black; }
        </style>
    </head>
    <body>
        <div id="info">
            <h2>BX-10 3D 物理競技場</h2>
            <p>🔵 UX-15 SharkScale (38.16g / 1-60 LR)<br>🟣 CX-01 Unicorn Sting (36.2g / 3-60 LR)</p>
        </div>
        <div id="container"></div>

        <script type="module">
            import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.module.js';

            // 參數接收
            const UX_RPM = __UX_RPM__;
            const CX_RPM = __CX_RPM__;
            const UX_ANG = __UX_ANG__;
            const CX_ANG = __CX_ANG__;

            // 初始化場景
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(45, window.innerWidth / 600, 0.1, 1000);
            camera.position.set(0, 50, 65);
            camera.lookAt(0, 0, 0);
            
            const renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, 600);
            document.getElementById('container').appendChild(renderer.domElement);

            // 燈光設置 (凸顯立體感)
            const light = new THREE.PointLight(0xffffff, 1.2);
            light.position.set(10, 40, 20);
            scene.add(light);
            scene.add(new THREE.AmbientLight(0x555555));

            // ==========================================
            // 1. 構建 BX-10 3D 競技場
            // ==========================================
            // 底部盆地
            const stadiumGeo = new THREE.CylinderGeometry(25, 25, 2, 64);
            const stadiumMat = new THREE.MeshPhongMaterial({ color: 0xcccccc });
            const stadium = new THREE.Mesh(stadiumGeo, stadiumMat);
            stadium.position.y = -1;
            scene.add(stadium);

            // 綠色極限加速軌道 (帶有缺口設計)
            const railRadius = 18;
            const railGeo = new THREE.TorusGeometry(railRadius, 0.8, 16, 64);
            const pos = railGeo.attributes.position;
            for (let i = 0; i < pos.count; i++) {
                let x = pos.getX(i); let y = pos.getY(i); let z = pos.getZ(i);
                let angle = Math.atan2(z, x);
                // 模擬真實的向內凹陷軌道
                if (Math.abs(angle) < 0.5 || Math.abs(angle - Math.PI) < 0.5) {
                    x *= 0.92; z *= 0.92;
                }
                pos.setXYZ(i, x, y, z);
            }
            railGeo.computeVertexNormals();
            const railMat = new THREE.MeshPhongMaterial({ color: 0x00ff44 });
            const rail = new THREE.Mesh(railGeo, railMat);
            rail.rotation.x = Math.PI / 2;
            rail.position.y = 0.5;
            scene.add(rail);

            // ==========================================
            // 2. 構建 3D 非對稱戰鬥陀螺
            // ==========================================
            function createUX15(tiltAngle) {
                const group = new THREE.Group();
                // 1-60 輪盤 (高度 6)
                const ratchetGeo = new THREE.CylinderGeometry(1.8, 1.8, 1.5, 16);
                const ratchetMat = new THREE.MeshPhongMaterial({ color: 0x333333 });
                const ratchet = new THREE.Mesh(ratchetGeo, ratchetMat);
                ratchet.position.y = 1.0;
                
                // UX-15 戰刃 (粉藍色，帶有上挑斜角)
                const bladeGeo = new THREE.CylinderGeometry(3.5, 3.2, 1.2, 16);
                const bladeMat = new THREE.MeshPhongMaterial({ color: 0xB0E0E6 });
                const blade = new THREE.Mesh(bladeGeo, bladeMat);
                blade.position.y = 2.0;
                // 模擬鯊魚上挑鰭 (斜角)
                blade.rotation.x = 0.1; 
                
                group.add(ratchet); group.add(blade);
                group.rotation.z = tiltAngle; // 發射傾角
                scene.add(group);
                return group;
            }

            function createCX01(tiltAngle) {
                const group = new THREE.Group();
                // 3-60 輪盤 (高度 6)
                const ratchetGeo = new THREE.CylinderGeometry(2.0, 2.0, 1.5, 16);
                const ratchetMat = new THREE.MeshPhongMaterial({ color: 0x555555 });
                const ratchet = new THREE.Mesh(ratchetGeo, ratchetMat);
                ratchet.position.y = 1.0;
                
                // CX-01 不對稱戰刃 (粉紫色)
                const bladeGeo = new THREE.CylinderGeometry(3.6, 3.6, 1.0, 16);
                const bladeMat = new THREE.MeshPhongMaterial({ color: 0xDDA0DD });
                const blade = new THREE.Mesh(bladeGeo, bladeMat);
                blade.position.y = 2.0;
                
                // 模擬 Unicorn Peak (突出的 3g 攻擊角)
                const peakGeo = new THREE.BoxGeometry(2, 1, 4);
                const peakMat = new THREE.MeshPhongMaterial({ color: 0xff3366 }); // 紅色標記攻擊點
                const peak = new THREE.Mesh(peakGeo, peakMat);
                peak.position.set(3, 2.0, 0);
                
                group.add(ratchet); group.add(blade); group.add(peak);
                group.rotation.z = tiltAngle;
                scene.add(group);
                return group;
            }

            const beyUX = createUX15(UX_ANG);
            beyUX.position.set(-10, 0, 5);
            let vUX = new THREE.Vector3(Math.random()*1.5, 0, Math.random()*1.5);
            let rpmUX = UX_RPM / 1000;

            const beyCX = createCX01(CX_ANG);
            beyCX.position.set(10, 0, -5);
            let vCX = new THREE.Vector3(-Math.random()*1.5, 0, -Math.random()*1.5);
            let rpmCX = CX_RPM / 1000;

            // ==========================================
            // 3. 真實物理與加速帶 (X-Dash) 引擎
            // ==========================================
            function animate() {
                requestAnimationFrame(animate);

                // 物理衰減
                rpmUX *= 0.998; rpmCX *= 0.998;
                vUX.multiplyScalar(0.99); vCX.multiplyScalar(0.99);

                // 自轉
                beyUX.rotation.y -= rpmUX * 0.2;
                beyCX.rotation.y -= rpmCX * 0.2;

                // 盆地重力 (向中央滑落)
                vUX.x -= beyUX.position.x * 0.002; vUX.z -= beyUX.position.z * 0.002;
                vCX.x -= beyCX.position.x * 0.002; vCX.z -= beyCX.position.z * 0.002;

                // 布朗運動 (受轉速與傾角影響)
                const chaosUX = UX_ANG > 0 ? 0.8 : 0.2;
                const chaosCX = CX_ANG > 0 ? 0.8 : 0.2;
                vUX.x += (Math.random() - 0.5) * chaosUX * (rpmUX/10);
                vUX.z += (Math.random() - 0.5) * chaosUX * (rpmUX/10);
                vCX.x += (Math.random() - 0.5) * chaosCX * (rpmCX/10);
                vCX.z += (Math.random() - 0.5) * chaosCX * (rpmCX/10);

                // Xtreme Line 切線加速 (X-Dash Physics)
                function applyXDash(bey, v) {
                    const dist = Math.sqrt(bey.position.x**2 + bey.position.z**2);
                    // 擦入半徑 17~19 的軌道
                    if (dist > 17 && dist < 19) {
                        // 計算切線向量 (Tangent)
                        let tangentX = -bey.position.z;
                        let tangentZ = bey.position.x;
                        // 正規化
                        let len = Math.sqrt(tangentX**2 + tangentZ**2);
                        tangentX /= len; tangentZ /= len;
                        
                        // 將速度轉向切線並瞬間放大 1.5 倍 (模擬 LR 軸心咬合齒輪)
                        v.x = v.x * 0.5 + tangentX * 2.5;
                        v.z = v.z * 0.5 + tangentZ * 2.5;
                        
                        // 稍微抬高 Z 軸模擬爬上軌道
                        bey.position.y = 0.5;
                    } else {
                        bey.position.y = 0; // 回到地面
                    }
                }
                applyXDash(beyUX, vUX);
                applyXDash(beyCX, vCX);

                // 更新位置
                beyUX.position.add(vUX.clone().multiplyScalar(0.4));
                beyCX.position.add(vCX.clone().multiplyScalar(0.4));

                // 邊界防禦
                if (Math.hypot(beyUX.position.x, beyUX.position.z) > 23) vUX.multiplyScalar(-0.5);
                if (Math.hypot(beyCX.position.x, beyCX.position.z) > 23) vCX.multiplyScalar(-0.5);

                // 3D 碰撞判定 (包含剛體體積)
                if (beyUX.position.distanceTo(beyCX.position) < 7.0) {
                    let tempV = vUX.clone();
                    // 質量影響反作用力 (UX-15 較重，CX-01 彈更遠)
                    vUX.copy(vCX).multiplyScalar(1.0);
                    vCX.copy(tempV).multiplyScalar(1.3);
                    
                    // 防重疊推開
                    beyUX.position.add(vUX.clone().multiplyScalar(0.2));
                    beyCX.position.add(vCX.clone().multiplyScalar(0.2));
                }

                renderer.render(scene, camera);
            }
            animate();
        </script>
    </body>
    </html>
    """
    
    # 變數注入
    html_code = html_template.replace("__UX_RPM__", str(ux_rpm)).replace("__CX_RPM__", str(cx_rpm))
    html_code = html_code.replace("__UX_ANG__", str(ux_angle)).replace("__CX_ANG__", str(cx_angle))
    
    components.html(html_code, height=620, scrolling=False)
    
else:
    st.info("請設定左側參數，然後點擊 **🚀 GO SHOOT!** 啟動 3D 引擎。")
