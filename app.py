<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mon Carnet de Recettes Virtuel & Nutrition</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 text-slate-800 min-h-screen pb-12">

  <!-- En-tête -->
  <header class="bg-indigo-600 text-white p-4 shadow-md sticky top-0 z-40">
    <div class="max-w-4xl mx-auto flex justify-between items-center">
      <h1 class="text-xl font-bold flex items-center gap-2">
        "🍳 Mes Recettes & Macros IA"
      </h1>
      <button onclick="toggleKeyModal()" class="text-sm bg-indigo-700 hover:bg-indigo-800 px-3 py-1.5 rounded-lg transition">
        "🔑 Clé API Gemini"
      </button>
    </div>
  </header>

  <main class="max-w-4xl mx-auto p-4 space-y-6">

    <!-- Formulaire d'extraction -->
    <section class="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
      <h2 class="text-lg font-semibold mb-2 text-slate-800">Ajouter une recette</h2>
      <p class="text-sm text-slate-500 mb-4">
        Colle le texte d'une publication OU importe directement une vidéo. L'IA extraira la recette, les calories et les macros.
      </p>

      <!-- Zone texte -->
      <textarea id="recipeInput" rows="3" class="w-full p-3 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none mb-3" placeholder="Colle le texte ou la description ici..."></textarea>

      <!-- Zone import vidéo -->
      <div class="border-2 border-dashed border-indigo-200 bg-indigo-50/50 p-4 rounded-lg mb-4 text-center">
        <label for="videoInput" class="cursor-pointer block">
          <span class="text-indigo-600 font-medium text-sm">🎥 Choisir ou déposer une vidéo</span>
          <span class="block text-xs text-slate-400 mt-1">Formats acceptés : MP4, MOV (max 20Mo conseillé)</span>
        </label>
        <input type="file" id="videoInput" accept="video/*" class="hidden" onchange="updateVideoLabel(this)">
        <p id="videoFileName" class="text-xs font-semibold text-indigo-700 mt-2 hidden"></p>
      </div>

      <div class="mt-3 flex justify-between items-center">
        <span id="statusMessage" class="text-xs text-slate-500"></span>
        <button onclick="extractRecipe()" id="btnExtract" class="bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium px-5 py-2 rounded-lg transition">
          "✨ Extraire avec Macros & Calories"
        </button>
      </div>
    </section>

    <!-- Liste des recettes -->
    <section>
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold">Mes Recettes (<span id="recipeCount">0</span>)</h2>
        <input type="text" id="searchInput" oninput="renderRecipes()" placeholder="Rechercher..." class="text-sm p-2 border border-slate-300 rounded-lg w-48 focus:outline-none focus:ring-2 focus:ring-indigo-500">
      </div>

      <div id="recipesContainer" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Cartes affichées dynamiquement -->
      </div>
    </section>

  </main>

  <!-- Modal Clé API -->
  <div id="keyModal" class="fixed inset-0 bg-black/50 hidden flex items-center justify-center p-4 z-50">
    <div class="bg-white p-6 rounded-xl max-w-md w-full space-y-4">
      <h3 class="text-lg font-bold">Clé API Google Gemini</h3>
      <p class="text-xs text-slate-600">
        Colle ta clé API gratuite récupérée sur <a href="https://aistudio.google.com/" target="_blank" class="text-indigo-600 underline">Google AI Studio</a>.
      </p>
      <input type="password" id="apiKeyInput" placeholder="Colle ta clé API ici..." class="w-full p-2 border border-slate-300 rounded-lg text-sm">
      <div class="flex justify-end gap-2">
        <button onclick="toggleKeyModal()" class="px-3 py-1.5 text-sm text-slate-600">Annuler</button>
        <button onclick="saveApiKey()" class="px-4 py-1.5 text-sm bg-indigo-600 text-white rounded-lg">Enregistrer</button>
      </div>
    </div>
  </div>

  <!-- Modal d'édition manuelle complète -->
  <div id="editModal" class="fixed inset-0 bg-black/50 hidden flex items-center justify-center p-4 z-50">
    <div class="bg-white p-6 rounded-xl max-w-lg w-full space-y-4 max-h-[90vh] overflow-y-auto">
      <h3 class="text-lg font-bold text-slate-800">Modifier la recette</h3>
      
      <input type="hidden" id="editRecipeId">
      
      <div>
        <label class="block text-xs font-semibold text-slate-600 mb-1">Titre du plat</label>
        <input type="text" id="editTitle" class="w-full p-2 border border-slate-300 rounded-lg text-sm">
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-xs font-semibold text-slate-600 mb-1">Temps de prép.</label>
          <input type="text" id="editPrepTime" class="w-full p-2 border border-slate-300 rounded-lg text-sm" placeholder="ex: 20 min">
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-600 mb-1">Portions de base</label>
          <input type="number" id="editBaseServings" min="1" max="12" class="w-full p-2 border border-slate-300 rounded-lg text-sm">
        </div>
      </div>

      <!-- Macros / Nutrition -->
      <div class="p-3 bg-slate-50 border border-slate-200 rounded-lg space-y-2">
        <p class="text-xs font-bold text-slate-700">Nutrition (par portion) :</p>
        <div class="grid grid-cols-4 gap-2">
          <div>
            <label class="block text-[10px] text-slate-500">Calories (kcal)</label>
            <input type="number" id="editCalories" class="w-full p-1.5 border border-slate-300 rounded text-xs">
          </div>
          <div>
            <label class="block text-[10px] text-slate-500">Protéines (g)</label>
            <input type="number" id="editProteins" class="w-full p-1.5 border border-slate-300 rounded text-xs">
          </div>
          <div>
            <label class="block text-[10px] text-slate-500">Glucides (g)</label>
            <input type="number" id="editCarbs" class="w-full p-1.5 border border-slate-300 rounded text-xs">
          </div>
          <div>
            <label class="block text-[10px] text-slate-500">Lipides (g)</label>
            <input type="number" id="editFats" class="w-full p-1.5 border border-slate-300 rounded text-xs">
          </div>
        </div>
      </div>

      <div>
        <label class="block text-xs font-semibold text-slate-600 mb-1">Ingrédients (1 par ligne)</label>
        <textarea id="editIngredients" rows="4" class="w-full p-2 border border-slate-300 rounded-lg text-sm"></textarea>
      </div>

      <div>
        <label class="block text-xs font-semibold text-slate-600 mb-1">Étapes de préparation (1 par ligne)</label>
        <textarea id="editSteps" rows="4" class="w-full p-2 border border-slate-300 rounded-lg text-sm"></textarea>
      </div>

      <div>
        <label class="block text-xs font-semibold text-slate-600 mb-1">Notes & Commentaires personnels</label>
        <textarea id="editComment" rows="2" class="w-full p-2 border border-slate-300 rounded-lg text-sm" placeholder="Ajouter une remarque personnelle..."></textarea>
      </div>

      <div class="flex justify-end gap-2 pt-2">
        <button onclick="closeEditModal()" class="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg">Annuler</button>
        <button onclick="saveManualEdit()" class="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg">Enregistrer</button>
      </div>
    </div>
  </div>

  <script>
    let recipes = JSON.parse(localStorage.getItem('my_recipes') || '[]');
    let apiKey = localStorage.getItem('gemini_api_key') || '';

    function toggleKeyModal() {
      const modal = document.getElementById('keyModal');
      modal.classList.toggle('hidden');
      if (!modal.classList.contains('hidden')) {
        document.getElementById('apiKeyInput').value = apiKey;
      }
    }

    function saveApiKey() {
      apiKey = document.getElementById('apiKeyInput').value.trim();
      localStorage.setItem('gemini_api_key', apiKey);
      toggleKeyModal();
      alert('Clé API enregistrée !');
    }

    function saveRecipes() {
      localStorage.setItem('my_recipes', JSON.stringify(recipes));
      renderRecipes();
    }

    function updateVideoLabel(input) {
      const label = document.getElementById('videoFileName');
      if (input.files && input.files[0]) {
        label.innerText = "Fichier sélectionné : " + input.files[0].name;
        label.classList.remove('hidden');
      } else {
        label.classList.add('hidden');
      }
    }

    function fileToBase64(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result.split(',')[1]);
        reader.onerror = error => reject(error);
      });
    }

    // Extraction IA avec Calories & Macros
    async function extractRecipe() {
      const textInput = document.getElementById('recipeInput').value.trim();
      const videoFileInput = document.getElementById('videoInput');
      const videoFile = videoFileInput.files[0];
      const status = document.getElementById('statusMessage');

      if (!textInput && !videoFile) {
        alert('Veuillez coller un texte ou sélectionner un fichier vidéo.');
        return;
      }

      if (!apiKey) {
        alert('Veuillez configurer votre clé API Gemini.');
        toggleKeyModal();
        return;
      }

      status.innerText = "Analyse par l'IA et calcul des valeurs nutritionnelles...";

      const promptText = `Analyse le contenu (texte ou vidéo/audio) et extrait les informations sous forme de JSON strict avec exactement ces champs:
      "title" (nom du plat),
      "prepTime" (ex: "20 min"),
      "baseServings" (un NOMBRE entier représentant le nombre de portions de la recette d'origine, ex: 4),
      "ingredients" (tableau de chaînes avec quantités claires, ex: ["200g de chocolat", "3 oeufs"]),
      "steps" (tableau de chaînes),
      "calories" (estimation numérique des calories PAR PORTION en kcal, ex: 350),
      "proteins" (estimation numérique des protéines PAR PORTION en grammes, ex: 12),
      "carbs" (estimation numérique des glucides PAR PORTION en grammes, ex: 45),
      "fats" (estimation numérique des lipides PAR PORTION en grammes, ex: 15).`;

      let parts = [{ text: promptText }];

      if (textInput) {
        parts.push({ text: `Texte fourni : ${textInput}` });
      }

      if (videoFile) {
        try {
          const base64Data = await fileToBase64(videoFile);
          parts.push({
            inline_data: {
              mime_type: videoFile.type || "video/mp4",
              data: base64Data
            }
          });
        } catch (e) {
          status.innerText = "Erreur de lecture du fichier vidéo.";
          return;
        }
      }

      try {
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ contents: [{ parts: parts }] })
        });

        const data = await response.json();

        if (!data.candidates || !data.candidates[0]) {
          throw new Error("Réponse de l'IA invalide");
        }

        const rawResponse = data.candidates[0].content.parts[0].text;
        const cleanJson = rawResponse.replace(/```json/g, '').replace(/```/g, '').trim();
        const extracted = JSON.parse(cleanJson);

        const baseServings = parseInt(extracted.baseServings) || 4;

        recipes.unshift({
          id: Date.now(),
          title: extracted.title || 'Nouvelle recette',
          prepTime: extracted.prepTime || 'Non précisé',
          baseServings: baseServings,
          currentServings: baseServings,
          ingredients: extracted.ingredients || [],
          steps: extracted.steps || [],
          calories: parseInt(extracted.calories) || 0,
          proteins: parseInt(extracted.proteins) || 0,
          carbs: parseInt(extracted.carbs) || 0,
          fats: parseInt(extracted.fats) || 0,
          rating: 0,
          comment: ''
        });

        saveRecipes();
        document.getElementById('recipeInput').value = '';
        videoFileInput.value = '';
        document.getElementById('videoFileName').classList.add('hidden');
        status.innerText = 'Recette ajoutée avec succès !';
      } catch (err) {
        console.error(err);
        status.innerText = "Erreur lors de l'extraction. Vérifiez la taille de la vidéo ou votre clé API.";
      }
    }

    // Ajustement dynamique des ingrédients selon le nombre de personnes
    function scaleIngredient(ingredientStr, ratio) {
      // Expression régulière pour repérer les nombres (entiers ou décimaux)
      return ingredientStr.replace(/(\d+([.,]\d+)?)/g, (match) => {
        let val = parseFloat(match.replace(',', '.'));
        let newParam = Math.round((val * ratio) * 10) / 10;
        return newParam;
      });
    }

    function changeServings(recipeId, delta) {
      const recipe = recipes.find(r => r.id === recipeId);
      if (!recipe) return;

      let newServings = (recipe.currentServings || recipe.baseServings || 4) + delta;
      if (newServings < 1) newServings = 1;
      if (newServings > 12) newServings = 12;

      recipe.currentServings = newServings;
      saveRecipes();
    }

    function setRating(recipeId, rating) {
      const recipe = recipes.find(r => r.id === recipeId);
      if (!recipe) return;
      recipe.rating = rating;
      saveRecipes();
    }

    // Modal d'édition
    function openEditModal(id) {
      const recipe = recipes.find(r => r.id === id);
      if (!recipe) return;

      document.getElementById('editRecipeId').value = recipe.id;
      document.getElementById('editTitle').value = recipe.title;
      document.getElementById('editPrepTime').value = recipe.prepTime;
      document.getElementById('editBaseServings').value = recipe.baseServings || 4;
      document.getElementById('editCalories').value = recipe.calories || 0;
      document.getElementById('editProteins').value = recipe.proteins || 0;
      document.getElementById('editCarbs').value = recipe.carbs || 0;
      document.getElementById('editFats').value = recipe.fats || 0;
      document.getElementById('editIngredients').value = recipe.ingredients.join('\n');
      document.getElementById('editSteps').value = recipe.steps.join('\n');
      document.getElementById('editComment').value = recipe.comment || '';

      document.getElementById('editModal').classList.remove('hidden');
    }

    function closeEditModal() {
      document.getElementById('editModal').classList.add('hidden');
    }

    function saveManualEdit() {
      const id = parseInt(document.getElementById('editRecipeId').value);
      const recipeIndex = recipes.findIndex(r => r.id === id);

      if (recipeIndex === -1) return;

      const ingredientsText = document.getElementById('editIngredients').value.trim();
      const stepsText = document.getElementById('editSteps').value.trim();

      recipes[recipeIndex] = {
        ...recipes[recipeIndex],
        title: document.getElementById('editTitle').value.trim() || 'Sans titre',
        prepTime: document.getElementById('editPrepTime').value.trim() || 'Non précisé',
        baseServings: parseInt(document.getElementById('editBaseServings').value) || 4,
        calories: parseInt(document.getElementById('editCalories').value) || 0,
        proteins: parseInt(document.getElementById('editProteins').value) || 0,
        carbs: parseInt(document.getElementById('editCarbs').value) || 0,
        fats: parseInt(document.getElementById('editFats').value) || 0,
        ingredients: ingredientsText ? ingredientsText.split('\n').map(i => i.trim()).filter(i => i.length > 0) : [],
        steps: stepsText ? stepsText.split('\n').map(s => s.trim()).filter(s => s.length > 0) : [],
        comment: document.getElementById('editComment').value.trim()
      };

      saveRecipes();
      closeEditModal();
    }

    function deleteRecipe(id) {
      if (confirm('Voulez-vous vraiment supprimer cette recette ?')) {
        recipes = recipes.filter(r => r.id !== id);
        saveRecipes();
      }
    }

    // Affichage des cartes de recettes
    function renderRecipes() {
      const container = document.getElementById('recipesContainer');
      const search = document.getElementById('searchInput').value.toLowerCase();
      document.getElementById('recipeCount').innerText = recipes.length;

      container.innerHTML = '';

      const filtered = recipes.filter(r => 
        r.title.toLowerCase().includes(search) || 
        r.ingredients.some(i => i.toLowerCase().includes(search))
      );

      if (filtered.length === 0) {
        container.innerHTML = `<p class="text-sm text-slate-400 col-span-2 text-center py-8">Aucune recette enregistrée.</p>`;
        return;
      }

      filtered.forEach(r => {
        const baseServings = r.baseServings || 4;
        const currentServings = r.currentServings || baseServings;
        const ratio = currentServings / baseServings;

        // Calcul des ingrédients proportionnels
        const ingList = r.ingredients.map(i => `<li class="text-xs text-slate-600">• ${scaleIngredient(i, ratio)}</li>`).join('');
        const stepList = r.steps.map((s, idx) => `<li class="text-xs text-slate-600"><span class="font-bold text-indigo-600">${idx+1}.</span> ${s}</li>`).join('');

        // Affichage des étoiles de notation
        let starsHtml = '';
        for (let i = 1; i <= 5; i++) {
          const starColor = i <= (r.rating || 0) ? 'text-amber-400' : 'text-slate-300';
          starsHtml += `<button onclick="setRating(${r.id}, ${i})" class="${starColor} text-sm focus:outline-none">★</button>`;
        }

        const card = document.createElement('div');
        card.className = 'bg-white p-5 rounded-xl shadow-sm border border-slate-200 flex flex-col justify-between space-y-4';

        card.innerHTML = `
          <div>
            <!-- En-tête Carte -->
            <div class="flex justify-between items-start gap-2">
              <div>
                <h3 class="font-bold text-slate-800">${r.title}</h3>
                <div class="flex items-center gap-1 mt-1">${starsHtml}</div>
              </div>
              <div class="flex gap-2">
                <button onclick="openEditModal(${r.id})" class="text-indigo-600 hover:text-indigo-800 text-xs font-medium">✏️ Éditer</button>
                <button onclick="deleteRecipe(${r.id})" class="text-red-400 hover:text-red-600 text-xs font-medium">Supprimer</button>
              </div>
            </div>

            <!-- Infos Temps & Portions Réglables -->
            <div class="flex items-center justify-between bg-slate-50 p-2.5 rounded-lg my-3 border border-slate-100">
              <span class="text-xs text-slate-500">⏱️ ${r.prepTime}</span>
              
              <div class="flex items-center gap-2">
                <span class="text-xs font-semibold text-slate-600">Portions:</span>
                <button onclick="changeServings(${r.id}, -1)" class="w-6 h-6 bg-white border border-slate-300 rounded text-xs font-bold text-slate-600 hover:bg-slate-100 flex items-center justify-center">−</button>
                <span class="text-xs font-bold text-indigo-600">${currentServings} pers.</span>
                <button onclick="changeServings(${r.id}, 1)" class="w-6 h-6 bg-white border border-slate-300 rounded text-xs font-bold text-slate-600 hover:bg-slate-100 flex items-center justify-center">+</button>
              </div>
            </div>

            <!-- Bloc Calories & Macros -->
            <div class="grid grid-cols-4 gap-1 text-center bg-indigo-50/60 p-2 rounded-lg mb-3 text-xs border border-indigo-100">
              <div>
                <span class="block text-[10px] text-indigo-400 font-semibold">CALORIES</span>
                <span class="font-bold text-indigo-900">${r.calories || 0} <span class="text-[9px] font-normal">kcal</span></span>
              </div>
              <div>
                <span class="block text-[10px] text-indigo-400 font-semibold">PROTÉINES</span>
                <span class="font-bold text-indigo-900">${r.proteins || 0}g</span>
              </div>
              <div>
                <span class="block text-[10px] text-indigo-400 font-semibold">GLUCIDES</span>
                <span class="font-bold text-indigo-900">${r.carbs || 0}g</span>
              </div>
              <div>
                <span class="block text-[10px] text-indigo-400 font-semibold">LIPIDES</span>
                <span class="font-bold text-indigo-900">${r.fats || 0}g</span>
              </div>
            </div>

            <!-- Ingrédients -->
            <div class="mt-3">
              <p class="text-xs font-semibold text-slate-700">Ingrédients :</p>
              <ul class="mt-1 space-y-0.5">${ingList}</ul>
            </div>

            <!-- Étapes -->
            <div class="mt-3">
              <p class="text-xs font-semibold text-slate-700">Préparation :</p>
              <ul class="mt-1 space-y-1">${stepList}</ul>
            </div>

            <!-- Remarques / Remarques personnelles -->
            ${r.comment ? `
              <div class="mt-3 p-2.5 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-900">
                <span class="font-bold">💬 Note :</span> ${r.comment}
              </div>
            ` : ''}
          </div>
        `;
        container.appendChild(card);
      });
    }

    renderRecipes();
  </script>
</body>
</html>
