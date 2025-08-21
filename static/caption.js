const imageInput = document.getElementById("imageInput");
const imagePreview = document.getElementById("imagePreview");
const generateBtn = document.getElementById("generateBtn");
const generatedCaption = document.getElementById("generatedCaption");
const copyBtn = document.getElementById("copyBtn");

// Show uploaded image in preview
imageInput.addEventListener("change", () => {
  const file = imageInput.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.innerHTML = `<img src="${e.target.result}" alt="Preview" style="max-width:100%; max-height:100%; border-radius:8px;">`;
    };
    reader.readAsDataURL(file);
  }
});

// Generate caption via Flask backend
generateBtn.addEventListener("click", async () => {
  const file = imageInput.files[0];
  if (!file) {
    alert("Please select an image!");
    return;
  }
  const tone = document.getElementById("tone").value;
  const context = document.getElementById("context").value;
  const hashtags = document.getElementById("hashtags").checked;

  const reader = new FileReader();
  reader.onload = async function() {
    const base64Image = reader.result.split(',')[1];
    generatedCaption.textContent = "⏳ Generating caption…";

    try {
      const response = await fetch("/analyze", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          image: base64Image,
          type: "caption",
          tone: tone,
          context: context,
          hashtags: hashtags
        })
      });

      const data = await response.json();

      if (data.caption1 && data.caption2) {
        generatedCaption.innerHTML = `
          <p>✨ ${data.caption1}</p>
          <p>🌟 ${data.caption2}</p>
        `;
      } else if (data.caption1) {
        generatedCaption.textContent = data.caption1;
      } else if (data.error) {
        generatedCaption.textContent = "❌ " + data.error;
      } else {
        generatedCaption.textContent = "⚠ Error generating caption.";
      }

    } catch (error) {
      generatedCaption.textContent = "Error: " + error.message;
    }
  };
  reader.readAsDataURL(file);
});

// Copy caption(s) to clipboard
copyBtn.addEventListener("click", () => {
  const captionText = generatedCaption.innerText.trim();
  if (captionText && captionText !== "Your caption will appear here after generation.") {
    navigator.clipboard.writeText(captionText).then(() => {
      alert("✅ Caption(s) copied to clipboard!");
    }).catch(err => {
      console.error("Error copying caption: ", err);
    });
  } else {
    alert("⚠ Generate a caption first before copying!");
  }
});
