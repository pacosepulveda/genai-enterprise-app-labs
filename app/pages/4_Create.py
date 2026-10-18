import io
import json

import streamlit as st
from PIL import Image

from enterprise_genai.config import get_settings
from enterprise_genai.image_generation import generate_image


st.set_page_config(page_title="Create", page_icon="🎨", layout="wide")

st.title("🎨 Create — Visual Asset Generator")
st.caption(
    "M04-P03 + M04-P04 · Prompt → foundation model → activo visual sintético con procedencia"
)

st.warning(
    "Esta superficie genera contenido sintético. Las imágenes creadas aquí no deben tratarse "
    "como evidencias de una incidencia ni mezclarse con las entradas de Analyze."
)

DEFAULT_PROMPT = (
    "Professional editorial illustration for an internal enterprise training course about secure remote access. "
    "A remote employee working on a laptop at a clean home-office desk, abstract visual metaphor of an encrypted "
    "VPN tunnel connecting to a modern corporate network operations center in the background. "
    "Clear composition, realistic lighting, polished corporate visual style, blue and neutral palette, "
    "wide cinematic framing, no readable text, no logos, no brand names."
)

DEFAULT_NEGATIVE_PROMPT = (
    "readable text, captions, letters, logos, brand marks, watermark, low resolution, blurry image, "
    "distorted anatomy, duplicated objects, cluttered composition"
)

settings = get_settings()

left, right = st.columns([3, 2])

with left:
    purpose = st.selectbox(
        "Propósito del activo",
        [
            "internal_training_asset",
            "knowledge_base_illustration",
            "internal_presentation_asset",
        ],
        help="El propósito se guarda como metadato de procedencia; no se envía al modelo salvo que aparezca en el prompt.",
    )

    prompt = st.text_area(
        "Prompt",
        value=DEFAULT_PROMPT,
        height=220,
        help="Describe el objetivo visual, sujeto, contexto, composición y restricciones relevantes.",
    )

    negative_prompt = st.text_area(
        "Negative prompt",
        value=DEFAULT_NEGATIVE_PROMPT,
        height=120,
        help="Indica características que quieres desalentar. No es una garantía determinista.",
    )

with right:
    st.markdown("### Parámetros")
    aspect_ratio = st.selectbox(
        "Relación de aspecto",
        ["16:9", "1:1", "3:2", "2:3", "4:5", "5:4", "9:16", "21:9", "9:21"],
        index=0,
    )
    seed = st.number_input(
        "Seed",
        min_value=0,
        max_value=4_294_967_295,
        value=42,
        step=1,
        help="Mantén la seed para comparar prompts o cámbiala para explorar variantes.",
    )
    output_format = st.selectbox("Formato", ["png", "jpeg"], index=0)

    st.markdown("### Modelo")
    st.code(settings.bedrock_image_model_id or "No configurado", language=None)
    st.caption(f"Región: {settings.bedrock_image_region}")

    generate = st.button("Generar activo", type="primary", use_container_width=True)

if generate:
    if not prompt.strip():
        st.warning("Introduce un prompt antes de generar.")
        st.stop()

    with st.spinner("Generando imagen con Bedrock..."):
        try:
            result = generate_image(
                prompt,
                negative_prompt=negative_prompt.strip() or None,
                aspect_ratio=aspect_ratio,
                seed=int(seed),
                output_format=output_format,
            )
        except Exception as exc:
            st.error(f"No se pudo generar el activo: {exc}")
            st.stop()

    image = Image.open(io.BytesIO(result["image_bytes"]))

    provenance = {
        "synthetic": True,
        "purpose": purpose,
        "model_id": result["model_id"],
        "region": result["region"],
        "prompt": prompt,
        "negative_prompt": negative_prompt.strip() or None,
        "seed": result["seed"],
        "requested_seed": result["requested_seed"],
        "aspect_ratio": result["aspect_ratio"],
        "output_format": result["output_format"],
        "latency_ms": result["latency_ms"],
        "finish_reason": result["finish_reason"],
        "width": image.size[0],
        "height": image.size[1],
        "bytes": len(result["image_bytes"]),
    }

    st.success("Activo sintético generado correctamente.")

    image_col, meta_col = st.columns([3, 2])
    with image_col:
        st.image(result["image_bytes"], caption="Activo generado · contenido sintético", width="stretch")

    with meta_col:
        st.metric("Latencia", f"{result['latency_ms']} ms")
        st.metric("Seed devuelta", result["seed"])
        st.metric("Dimensiones", f"{image.size[0]} × {image.size[1]}")
        st.markdown("**Clasificación del activo**")
        st.code("synthetic = true", language=None)
        st.write(f"Propósito: `{purpose}`")

    st.subheader("Procedencia")
    st.json(provenance)

    image_extension = "jpg" if output_format == "jpeg" else "png"
    metadata_bytes = json.dumps(provenance, ensure_ascii=False, indent=2).encode("utf-8")

    d1, d2 = st.columns(2)
    with d1:
        st.download_button(
            "Descargar imagen",
            data=result["image_bytes"],
            file_name=f"generated_asset.{image_extension}",
            mime="image/jpeg" if output_format == "jpeg" else "image/png",
            use_container_width=True,
        )
    with d2:
        st.download_button(
            "Descargar metadatos JSON",
            data=metadata_bytes,
            file_name="generated_asset.json",
            mime="application/json",
            use_container_width=True,
        )

    with st.expander("🔎 Abrir la caja: request enviado al modelo"):
        st.json(result["request"])

    with st.expander("📦 Response metadata de Bedrock"):
        st.json(result["response_metadata"])

st.divider()
st.caption(
    "Analyze interpreta información observada. Create produce contenido sintético. "
    "Mantener ambas rutas separadas forma parte del diseño de la aplicación."
)
