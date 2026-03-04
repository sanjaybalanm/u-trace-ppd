import React, { useRef, useState, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Html, ContactShadows, Environment, Stars, Float } from '@react-three/drei';
import * as THREE from 'three';

// --- Styled 3D Label ---
const RiskLabel = ({ label, color }) => (
    <div style={{
        background: 'rgba(15, 23, 42, 0.9)',
        color: '#e2e8f0',
        padding: '8px 12px',
        borderRadius: '8px',
        fontSize: '12px',
        fontFamily: 'Inter, sans-serif',
        border: `1px solid ${color}`,
        boxShadow: `0 0 15px ${color}40`,
        backdropFilter: 'blur(4px)',
        transform: 'translate3d(-50%, -100%, 0)',
        pointerEvents: 'none',
        display: 'flex',
        alignItems: 'center',
        gap: '6px'
    }}>
        <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: color,
            boxShadow: `0 0 8px ${color}`
        }} />
        <span style={{ fontWeight: 600 }}>{label}</span>
    </div>
);

// --- Reusable Body Part Component ---
const BodyPart = ({ position, onClick, color, label, isTarget, scale = [1, 1, 1], geometryType = 'box', opacity = 0.9 }) => {
    const meshRef = useRef();
    const [hovered, setHover] = useState(false);

    // Pulse animation if this is a high-risk target
    useFrame((state) => {
        if (isTarget && meshRef.current) {
            const t = state.clock.getElapsedTime();
            const s = 1 + Math.sin(t * 4) * 0.03; // Subtle pulse
            meshRef.current.scale.set(scale[0] * s, scale[1] * s, scale[2] * s);

            // Dynamic emissive pulse
            const intensity = (Math.sin(t * 4) + 1) / 2;
            meshRef.current.material.emissiveIntensity = 0.4 + intensity * 0.6;
        } else if (hovered && meshRef.current) {
            meshRef.current.material.emissiveIntensity = 0.2;
        } else if (meshRef.current) {
            meshRef.current.material.emissiveIntensity = 0;
        }
    });

    // Geometry selection
    let geometry;
    if (geometryType === 'sphere') geometry = <sphereGeometry args={[0.5, 32, 32]} />;
    else if (geometryType === 'capsule') geometry = <capsuleGeometry args={[0.3, 1, 8, 16]} />;
    else if (geometryType === 'roundedBox') geometry = <boxGeometry args={[1, 1, 1]} />; // Using standard box but smooth shading via material
    else geometry = <boxGeometry args={[1, 1, 1]} />;

    // Material Color Logic
    // If Safe (Low risk) -> Use a Neutral "Holographic Blue/Grey" 
    // If Danger (High Risk) -> Use the passed color (Red/Orange)
    const displayColor = isTarget ? color : '#64748b';
    const emissiveColor = isTarget ? color : '#38bdf8';

    return (
        <group position={position}>
            <mesh
                ref={meshRef}
                scale={scale}
                onClick={onClick}
                onPointerOver={() => setHover(true)}
                onPointerOut={() => setHover(false)}
            >
                {geometry}
                <meshPhysicalMaterial
                    color={displayColor}
                    emissive={emissiveColor}
                    emissiveIntensity={isTarget ? 0.5 : 0}
                    metalness={0.8}
                    roughness={0.2}
                    transparent
                    opacity={isTarget ? 1 : 0.6}
                    clearcoat={1}
                    clearcoatRoughness={0.1}
                />
            </mesh>
            {(hovered || isTarget) && (
                <Html position={[0, scale[1] / 2 + 0.2, 0]} center distanceFactor={8}>
                    <RiskLabel label={label || 'Part'} color={isTarget ? color : '#38bdf8'} />
                </Html>
            )}
        </group>
    );
};

// --- Main 3D Model ---
const HumanModel = ({ riskFactors }) => {
    const group = useRef();

    // Auto-rotate
    useFrame(() => {
        if (group.current) {
            group.current.rotation.y += 0.002;
        }
    });

    const getRiskColor = (level) => {
        if (level === 'High') return '#ef4444'; // Red
        if (level === 'Medium') return '#f59e0b'; // Amber
        return '#10b981'; // Green
    };

    const inhalationColor = getRiskColor(riskFactors?.inhalation);
    const dermalColor = getRiskColor(riskFactors?.dermal);
    const ingestionColor = getRiskColor(riskFactors?.ingestion);
    const creatinineColor = getRiskColor(riskFactors?.creatinine);

    const isHighRisk = (level) => level === 'High' || level === 'Medium';

    return (
        <group ref={group} position={[0, -1.2, 0]}>
            <Float speed={2} rotationIntensity={0.1} floatIntensity={0.2}>

                {/* --- HEAD --- */}
                <BodyPart position={[0, 1.75, 0]} geometryType="sphere" scale={[0.5, 0.55, 0.5]} label="Head" />

                {/* --- NECK --- */}
                <BodyPart position={[0, 1.45, 0]} geometryType="cylinder" scale={[0.2, 0.2, 0.2]} />

                {/* --- TORSO (LUNGS - UPPER) --- */}
                <BodyPart
                    position={[0, 1.1, 0]}
                    scale={[0.7, 0.6, 0.35]}
                    geometryType="roundedBox"
                    label={`Lungs: ${riskFactors?.inhalation || 'Safe'}`}
                    color={inhalationColor}
                    isTarget={isHighRisk(riskFactors?.inhalation)}
                    opacity={0.9}
                />

                {/* --- ABDOMEN (LOWER TORSO) --- */}
                <BodyPart
                    position={[0, 0.6, 0]}
                    scale={[0.6, 0.5, 0.32]}
                    geometryType="roundedBox"
                    label={`Digestive: ${riskFactors?.ingestion || 'Safe'}`}
                    color={ingestionColor}
                    isTarget={isHighRisk(riskFactors?.ingestion)}
                />

                {/* --- SHOULDERS --- */}
                <BodyPart position={[-0.5, 1.25, 0]} geometryType="sphere" scale={[0.25, 0.25, 0.25]} color={dermalColor} isTarget={isHighRisk(riskFactors?.dermal)} />
                <BodyPart position={[0.5, 1.25, 0]} geometryType="sphere" scale={[0.25, 0.25, 0.25]} color={dermalColor} isTarget={isHighRisk(riskFactors?.dermal)} />

                {/* --- ARMS (DERMAL) --- */}
                {/* Left Arm */}
                <BodyPart position={[-0.6, 0.9, 0]} scale={[0.18, 0.6, 0.18]} geometryType="cylinder" label="Upper Arm" color={dermalColor} isTarget={isHighRisk(riskFactors?.dermal)} />
                <BodyPart position={[-0.7, 0.4, 0.1]} scale={[0.15, 0.5, 0.15]} geometryType="cylinder" label={`Skin: ${riskFactors?.dermal}`} color={dermalColor} isTarget={isHighRisk(riskFactors?.dermal)} />
                {/* Right Arm */}
                <BodyPart position={[0.6, 0.9, 0]} scale={[0.18, 0.6, 0.18]} geometryType="cylinder" label="Upper Arm" color={dermalColor} isTarget={isHighRisk(riskFactors?.dermal)} />
                <BodyPart position={[0.7, 0.4, 0.1]} scale={[0.15, 0.5, 0.15]} geometryType="cylinder" label={`Skin: ${riskFactors?.dermal}`} color={dermalColor} isTarget={isHighRisk(riskFactors?.dermal)} />

                {/* --- HIPS --- */}
                <BodyPart position={[0, 0.2, 0]} scale={[0.65, 0.3, 0.35]} geometryType="roundedBox" />

                {/* --- LEGS --- */}
                {/* Left Leg */}
                <BodyPart position={[-0.25, -0.4, 0]} scale={[0.22, 0.8, 0.22]} geometryType="cylinder" />
                <BodyPart position={[-0.25, -1.3, 0.05]} scale={[0.2, 0.9, 0.2]} geometryType="cylinder" />
                {/* Right Leg */}
                <BodyPart position={[0.25, -0.4, 0]} scale={[0.22, 0.8, 0.22]} geometryType="cylinder" />
                <BodyPart position={[0.25, -1.3, 0.05]} scale={[0.2, 0.9, 0.2]} geometryType="cylinder" />

                {/* --- KIDNEYS (Specific Highlighting) --- */}
                {riskFactors?.creatinine && (
                    <>
                        <BodyPart position={[0.2, 0.7, -0.15]} scale={[0.15, 0.25, 0.1]} geometryType="sphere" label="Kidney" color={creatinineColor} isTarget={isHighRisk(riskFactors?.creatinine)} />
                        <BodyPart position={[-0.2, 0.7, -0.15]} scale={[0.15, 0.25, 0.1]} geometryType="sphere" label="Kidney" color={creatinineColor} isTarget={isHighRisk(riskFactors?.creatinine)} />
                    </>
                )}

            </Float>
        </group>
    );
};

const HealthAvatar = ({ riskFactors }) => {
    return (
        <div style={{ width: '100%', height: '500px', background: 'transperent', borderRadius: '12px' }}>
            <Canvas camera={{ position: [0, 1, 5], fov: 45 }}>
                {/* Visual Environment */}
                <ambientLight intensity={0.4} />
                <pointLight position={[10, 10, 10]} intensity={1} color="#38bdf8" />
                <pointLight position={[-10, 5, -10]} intensity={0.5} color="#c084fc" />
                <spotLight position={[0, 10, 0]} angle={0.5} penumbra={1} intensity={1} castShadow />

                <Stars radius={100} depth={50} count={2000} factor={4} saturation={0} fade speed={1} />

                <HumanModel riskFactors={riskFactors} />

                <ContactShadows position={[0, -2.5, 0]} opacity={0.4} scale={20} blur={2} far={4} color="#000" />
                <OrbitControls enableZoom={false} minPolarAngle={Math.PI / 3} maxPolarAngle={Math.PI / 1.8} />
            </Canvas>
            <div style={{
                textAlign: 'center',
                fontSize: '0.8rem',
                color: '#64748b',
                marginTop: '-30px',
                position: 'relative',
                zIndex: 10
            }}>
                Interactive 3D Digital Twin • Rotate to Explore
            </div>
        </div>
    );
};

export default HealthAvatar;
