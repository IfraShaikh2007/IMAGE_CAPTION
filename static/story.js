const imageInput = document.getElementById('image-input');
const generateBtn = document.getElementById('generate-btn');
const removeBtn = document.getElementById('remove-btn');
const toneSelect = document.getElementById('tone-select');
const storyTitle = document.getElementById('story-title-text');
const storyContent = document.getElementById('story-content');
const copyBtn = document.getElementById('copy-btn');
const uploadBox = document.getElementById('upload-box');
const uploadText = document.getElementById('upload-text');

let uploadedImage = null;

imageInput.addEventListener('change', (e) => {
  if (e.target.files.length > 0) {
    uploadedImage = e.target.files[0];
    generateBtn.disabled = false;
    removeBtn.style.display = 'inline-block';
    toneSelect.disabled = false;
    uploadText.textContent = `Selected: ${uploadedImage.name}`;
  } else {
    resetUpload();
  }
});

removeBtn.addEventListener('click', () => {
  resetUpload();
});

function resetUpload() {
  uploadedImage = null;
  imageInput.value = '';
  generateBtn.disabled = true;
  removeBtn.style.display = 'none';
  toneSelect.disabled = true;
  uploadText.textContent = 'Drop or paste an image';
  storyTitle.textContent = 'Story Title';
  storyContent.textContent = 'Your generated story will appear here based on the uploaded image.';
  toneSelect.value = 'neutral';
}

generateBtn.addEventListener('click', async () => {
  if (!uploadedImage) return;
  const tone = toneSelect.value;

  const reader = new FileReader();
  reader.onload = async function() {
    const base64Image = reader.result.split(',')[1];
    storyContent.textContent = "⏳ Generating story…";
    try {
      const response = await fetch('/analyze', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          image: base64Image,
          type: "story",
          tone: tone
        })
      });
      const data = await response.json();
      storyTitle.textContent = data.story_title || "Generated Story";
      storyContent.textContent = data.story || data.error || "Error generating story.";
    } catch (error) {
      storyContent.textContent = "Error: " + error.message;
    }
  };
  reader.readAsDataURL(uploadedImage);
});

// Copy story text button
copyBtn.addEventListener('click', () => {
  navigator.clipboard.writeText(storyContent.textContent).then(() => {
    copyBtn.textContent = 'Copied!';
    setTimeout(() => { copyBtn.textContent = 'Copy'; }, 1500);
  });
});
