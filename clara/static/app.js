
/* CLARA Salud | Bilingual Interface v0.2
   IDE SpA — Open-source educational prototype.
   No user accounts or application-level response storage.
*/

(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);

  const messages = {
    es: {
      prototype: "Prototipo educativo",
      eyebrow: "TECNOLOGÍA PARA COMPRENDER MEJOR",
      heroTitle: "Tu salud merece respuestas claras.",
      heroDescription:
        "Haz preguntas, recibe información fundamentada y comprueba lo que has comprendido. CLARA te acompaña paso a paso, con explicaciones sencillas y sin juicios.",
      start: "Comenzar ahora",
      freeAccess: "Acceso gratuito · Sin registro",
      ourApproach: "NUESTRO ENFOQUE",
      stepOne: "Pregunta",
      stepOneDesc: "Expresa tus dudas libremente.",
      stepTwo: "Comprende",
      stepTwoDesc: "Recibe información clara y fundamentada.",
      stepThree: "Explica",
      stepThreeDesc: "Cuenta con tus palabras qué entendiste.",
      stepFour: "Aclara",
      stepFourDesc:
        "Revisa posibles malentendidos y vuelve a intentarlo.",
      trusted: "Fuentes identificadas",
      private: "Sin registro personal",
      languages: "Español e inglés",
      experienceLabel: "EXPLORA CLARA",
      experienceTitle: "Un espacio para resolver tus dudas.",
      experienceDescription:
        "Comienza con una pregunta o practica cómo explicar lo que comprendiste.",
      currentModule: "MÓDULO DISPONIBLE",
      moduleTitle: "Anticoncepción de emergencia",
      moduleDescription:
        "Información esencial sobre métodos, plazos, seguridad y dudas frecuentes.",
      moduleStatus: "Versión educativa piloto",
      importantTitle: "Información importante",
      importantText:
        "CLARA es una herramienta educativa experimental. Sus contenidos están pendientes de revisión clínica y no sustituyen una consulta médica.",
      urgentText:
        "Si necesitas anticoncepción de emergencia, atención por violencia sexual o tienes síntomas graves, busca atención sanitaria cuanto antes.",
      askTab: "Hacer una pregunta",
      learnTab: "Comprobar comprensión",
      askKicker: "CONVERSA CON CLARA",
      askTitle: "¿Qué te gustaría saber?",
      askDescription:
        "Escribe una pregunta sobre anticoncepción de emergencia. CLARA buscará una respuesta dentro de su biblioteca sanitaria.",
      questionLabel: "Tu pregunta",
      questionHelp: "No incluyas datos personales.",
      askButton: "Consultar",
      suggestionsTitle: "También puedes explorar",
      claraAnswers: "CLARA RESPONDE",
      continueLearning: "Para seguir comprendiendo",
      sourcesTitle: "Fuentes de información",
      learnKicker: "APRENDER COMPRENDIENDO",
      learnTitle: "Explica con tus propias palabras.",
      learnDescription:
        "Lee la información, explica qué comprendiste y recibe orientaciones para aclarar conceptos importantes.",
      lessonLabel: "Elige un tema",
      informationLabel: "INFORMACIÓN PARA COMPRENDER",
      yourTurn: "AHORA ES TU TURNO",
      explanationLabel: "Tu explicación",
      assessButton: "Revisar comprensión",
      feedbackLabel: "RETROALIMENTACIÓN",
      coverageLabel: "Índice heurístico de conceptos",
      feedbackDetails: "Revisemos algunos conceptos",
      scoreDisclaimer:
        "Resultado exploratorio basado en reglas lingüísticas. No es una evaluación clínica ni un indicador validado de aprendizaje.",
      retryButton: "Escribir una nueva explicación",
      missionLabel: "NUESTRA MISIÓN",
      missionTitle:
        "Informar no siempre significa comprender.",
      missionDescription:
        "CLARA busca transformar la comunicación sanitaria en una experiencia más clara, participativa y verificable. Aspiramos a contribuir a decisiones informadas de mujeres y adolescentes.",
      footerMessage: "Comprender para decidir.",
      openSource: "Tecnología abierta e independiente",
      footerDisclaimer:
        "Prototipo educativo en desarrollo. Contenidos pendientes de revisión clínica. No proporciona diagnósticos, prescripciones ni atención sanitaria individualizada.",
      questionPlaceholder:
        "Por ejemplo: ¿Cuánto tiempo tengo para utilizarla?",
      responsePlaceholder:
        "Escribe aquí lo que comprendiste...",
      initial: "Evaluación inicial",
      second: "Segunda explicación",
      asking: "Consultando...",
      assessing: "Revisando...",
      networkError:
        "No fue posible comunicarse con CLARA. Revisa la conexión e intenta nuevamente.",
      catalogError:
        "No se pudo cargar el contenido sanitario.",
      missingQuestion:
        "Escribe una pregunta antes de continuar.",
      missingResponse:
        "Escribe una explicación antes de continuar.",
      comparison: "Comparación entre explicaciones",
      before: "Primera evaluación",
      after: "Segunda evaluación",
      difference: "Diferencia del índice heurístico",
      notClinical:
        "Los cambios reflejan reglas automáticas, no una mejora clínica demostrada."
    },

    en: {
      prototype: "Educational prototype",
      eyebrow: "TECHNOLOGY FOR BETTER UNDERSTANDING",
      heroTitle: "Your health deserves clear answers.",
      heroDescription:
        "Ask questions, explore referenced information, and check what you have understood. CLARA guides you step by step with simple, nonjudgmental explanations.",
      start: "Get started",
      freeAccess: "Free access · No registration",
      ourApproach: "OUR APPROACH",
      stepOne: "Ask",
      stepOneDesc: "Share your questions freely.",
      stepTwo: "Understand",
      stepTwoDesc:
        "Receive clear, referenced information.",
      stepThree: "Explain",
      stepThreeDesc:
        "Describe what you understood in your own words.",
      stepFour: "Clarify",
      stepFourDesc:
        "Review possible misconceptions and try again.",
      trusted: "Identified sources",
      private: "No personal registration",
      languages: "Spanish and English",
      experienceLabel: "EXPLORE CLARA",
      experienceTitle: "A space to explore your questions.",
      experienceDescription:
        "Start with a question or practice explaining what you understood.",
      currentModule: "AVAILABLE MODULE",
      moduleTitle: "Emergency contraception",
      moduleDescription:
        "Essential information about methods, timing, safety, and frequently asked questions.",
      moduleStatus: "Educational pilot version",
      importantTitle: "Important information",
      importantText:
        "CLARA is an experimental educational tool. Content is pending clinical review and does not replace medical advice.",
      urgentText:
        "If you need emergency contraception, care after sexual violence, or help with serious symptoms, seek healthcare promptly.",
      askTab: "Ask a question",
      learnTab: "Check understanding",
      askKicker: "TALK WITH CLARA",
      askTitle: "What would you like to know?",
      askDescription:
        "Ask a question about emergency contraception. CLARA will look for an answer in its health information library.",
      questionLabel: "Your question",
      questionHelp: "Do not include personal information.",
      askButton: "Ask CLARA",
      suggestionsTitle: "You can also explore",
      claraAnswers: "CLARA ANSWERS",
      continueLearning: "Keep learning",
      sourcesTitle: "Information sources",
      learnKicker: "LEARNING THROUGH UNDERSTANDING",
      learnTitle: "Explain it in your own words.",
      learnDescription:
        "Read the information, describe what you understood, and receive guidance to clarify key concepts.",
      lessonLabel: "Choose a topic",
      informationLabel: "INFORMATION TO UNDERSTAND",
      yourTurn: "YOUR TURN",
      explanationLabel: "Your explanation",
      assessButton: "Check understanding",
      feedbackLabel: "FEEDBACK",
      coverageLabel: "Heuristic concept index",
      feedbackDetails: "Let's review some concepts",
      scoreDisclaimer:
        "Exploratory rule-based result. This is not a clinical assessment or a validated learning measure.",
      retryButton: "Write a new explanation",
      missionLabel: "OUR MISSION",
      missionTitle:
        "Providing information does not always mean being understood.",
      missionDescription:
        "CLARA aims to make health communication clearer, more participatory, and measurable. Our goal is to support informed decisions by women and adolescent girls.",
      footerMessage: "Understand to decide.",
      openSource: "Open and independent technology",
      footerDisclaimer:
        "Educational prototype under development. Content is pending clinical review. It does not provide diagnoses, prescriptions, or individualized medical care.",
      questionPlaceholder:
        "For example: How much time do I have?",
      responsePlaceholder:
        "Write what you understood here...",
      initial: "Initial assessment",
      second: "Second explanation",
      asking: "Searching...",
      assessing: "Checking...",
      networkError:
        "CLARA could not be reached. Check your connection and try again.",
      catalogError:
        "Health information could not be loaded.",
      missingQuestion:
        "Please enter a question first.",
      missingResponse:
        "Please write an explanation first.",
      comparison: "Comparing your explanations",
      before: "First assessment",
      after: "Second assessment",
      difference: "Difference in heuristic index",
      notClinical:
        "Changes reflect automated rules, not demonstrated clinical improvement."
    }
  };

  const state = {
    lang: "es",
    catalog: null,
    phase: "pre",
    baseline: null,
    requestVersion: 0,
    busyAsk: false,
    busyAssess: false
  };

  const t = (key) =>
    messages[state.lang][key] || key;

  function notice(message, isError = true) {
    const node = $("app-notice");
    node.textContent = message;
    node.classList.toggle("is-error", isError);
    node.hidden = !message;
  }

  function translate() {
    document.documentElement.lang = state.lang;

    document.title = state.lang === "es"
      ? "CLARA Salud | Comprender para decidir"
      : "CLARA Salud | Understand to decide";

    document.querySelectorAll("[data-i18n]")
      .forEach((node) => {
        const key = node.dataset.i18n;
        if (messages[state.lang][key]) {
          node.textContent = t(key);
        }
      });

    $("question-input").placeholder =
      t("questionPlaceholder");

    $("assessment-response").placeholder =
      t("responsePlaceholder");

    $("phase-indicator").textContent =
      t(state.phase === "pre" ? "initial" : "second");

    document.querySelectorAll(".lang-button")
      .forEach((button) => {
        const selected =
          button.dataset.lang === state.lang;

        button.classList.toggle("active", selected);
        button.setAttribute(
          "aria-pressed",
          String(selected)
        );
      });
  }

  async function api(url, options) {
    const response = await fetch(url, {
      cache: "no-store",
      headers: {
        "Accept": "application/json",
        ...(options
          ? { "Content-Type": "application/json" }
          : {})
      },
      ...options
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return response.json();
  }

  function showTab(name) {
    const isAsk = name === "ask";

    $("panel-ask").hidden = !isAsk;
    $("panel-learn").hidden = isAsk;

    [
      ["ask", isAsk],
      ["learn", !isAsk]
    ].forEach(([tab, active]) => {
      const button = $(`tab-${tab}`);

      button.classList.toggle("active", active);
      button.setAttribute(
        "aria-selected",
        String(active)
      );
      button.tabIndex = active ? 0 : -1;
    });

    notice("");
  }

  function clearAssessment() {
    state.phase = "pre";
    state.baseline = null;

    $("assessment-response").value = "";
    $("assessment-result").hidden = true;
    $("comparison-card").hidden = true;
    $("repeat-button").hidden = true;

    $("phase-indicator").textContent = t("initial");
  }

  function displayLesson() {
    if (!state.catalog) return;

    const lesson = state.catalog.lessons.find(
      (x) => x.id === $("lesson-select").value
    );

    if (!lesson) return;

    $("lesson-title").textContent = lesson.title;
    $("lesson-intro").textContent = lesson.intro;
    $("lesson-question").textContent = lesson.question;

    clearAssessment();
  }

  function populateCatalog(data) {
    const list = $("faq-list");
    const select = $("lesson-select");

    list.replaceChildren();
    select.replaceChildren();

    data.faqs.forEach((faq) => {
      const button = document.createElement("button");

      button.type = "button";
      button.textContent = faq.label;

      button.addEventListener("click", () => {
        $("question-input").value = faq.label;
        askQuestion();
      });

      list.append(button);
    });

    data.lessons.forEach((lesson) => {
      const option = document.createElement("option");

      option.value = lesson.id;
      option.textContent = lesson.title;

      select.append(option);
    });

    displayLesson();
  }

  async function loadCatalog() {
    const version = ++state.requestVersion;

    state.catalog = null;

    try {
      const data = await api(
        `/api/catalog?lang=${state.lang}`
      );

      if (version !== state.requestVersion) return;

      state.catalog = data;
      populateCatalog(data);

    } catch (error) {
      if (version === state.requestVersion) {
        notice(t("catalogError"));
      }
    }
  }

  function approvedSource(raw) {
    try {
      const url = new URL(raw);

      const allowed = [
        "www.who.int",
        "www.cdc.gov",
        "www.minsal.cl"
      ];

      if (
        url.protocol === "https:" &&
        allowed.includes(url.hostname)
      ) {
        return url.href;
      }

      return null;

    } catch {
      return null;
    }
  }

  function renderAnswer(result) {
    const card = $("answer-card");

    card.hidden = false;
    card.classList.toggle(
      "is-warning",
      Boolean(result.warning)
    );

    $("answer-title").textContent =
      result.title || "CLARA";

    $("answer-text").textContent =
      result.answer || "";

    $("answer-next-text").textContent =
      result.next || "";

    const sources = $("answer-sources-list");
    sources.replaceChildren();

    (result.sources || []).forEach((source) => {
      const url = approvedSource(source.url);

      if (!url) return;

      const link = document.createElement("a");

      link.href = url;
      link.textContent = source.name;
      link.target = "_blank";
      link.rel = "noopener noreferrer";

      sources.append(link);
    });

    card.scrollIntoView({
      behavior: "smooth",
      block: "nearest"
    });
  }

  async function askQuestion() {
    const question = $("question-input").value.trim();

    if (!question) {
      return notice(t("missingQuestion"));
    }

    if (state.busyAsk) return;

    notice("");
    state.busyAsk = true;

    $("ask-button").disabled = true;
    $("ask-button").textContent = t("asking");

    const version = state.requestVersion;

    try {
      const result = await api("/api/ask", {
        method: "POST",
        body: JSON.stringify({
          question,
          lang: state.lang
        })
      });

      if (version === state.requestVersion) {
        renderAnswer(result);
      }

    } catch {
      if (version === state.requestVersion) {
        notice(t("networkError"));
      }

    } finally {
      state.busyAsk = false;
      $("ask-button").disabled = false;
      $("ask-button").textContent = t("askButton");
    }
  }

  function comparison(first, second) {
    const box = $("comparison-card");
    box.replaceChildren();

    const title = document.createElement("h3");
    title.textContent = t("comparison");

    box.append(title);

    const change = second - first;
    const sign = change > 0 ? "+" : "";

    const unit = state.lang === "es"
      ? "puntos"
      : "points";

    const lines = [
      `${t("before")}: ${first}%`,
      `${t("after")}: ${second}%`,
      `${t("difference")}: ${sign}${change} ${unit}`,
      t("notClinical")
    ];

    lines.forEach((line) => {
      const p = document.createElement("p");
      p.textContent = line;
      box.append(p);
    });

    box.hidden = false;
  }

  function renderAssessment(result, initialPhase) {
    const card = $("assessment-result");

    card.hidden = false;
    card.dataset.status = result.status;

    $("result-summary").textContent =
      result.summary;

    const index = Math.max(
      0,
      Math.min(100, Number(result.score) || 0)
    );

    $("result-score").textContent = `${index}%`;

    $("result-progress-bar").style.width =
      `${index}%`;

    const feedback = $("feedback-list");
    feedback.replaceChildren();

    (result.feedback || []).forEach((message) => {
      const li = document.createElement("li");

      li.textContent = message;
      feedback.append(li);
    });

    if (initialPhase) {
      state.baseline = index;
      state.phase = "post";

      $("phase-indicator").textContent =
        t("second");

      $("repeat-button").hidden = false;
      $("comparison-card").hidden = true;

    } else {
      comparison(
        state.baseline ?? index,
        index
      );

      $("repeat-button").hidden = true;
    }

    card.scrollIntoView({
      behavior: "smooth",
      block: "nearest"
    });
  }

  async function assessResponse() {
    if (!state.catalog || state.busyAssess) return;

    const response =
      $("assessment-response").value.trim();

    if (!response) {
      return notice(t("missingResponse"));
    }

    notice("");

    const phase = state.phase;
    const lesson_id = $("lesson-select").value;
    const version = state.requestVersion;

    state.busyAssess = true;

    $("assess-button").disabled = true;
    $("assess-button").textContent = t("assessing");

    try {
      const result = await api("/api/assess", {
        method: "POST",
        body: JSON.stringify({
          lesson_id,
          response,
          phase,
          lang: state.lang
        })
      });

      if (
        version === state.requestVersion &&
        lesson_id === $("lesson-select").value
      ) {
        renderAssessment(
          result,
          phase === "pre"
        );
      }

    } catch {
      if (version === state.requestVersion) {
        notice(t("networkError"));
      }

    } finally {
      state.busyAssess = false;
      $("assess-button").disabled = false;
      $("assess-button").textContent =
        t("assessButton");
    }
  }

  function changeLanguage(language) {
    if (
      !messages[language] ||
      language === state.lang
    ) {
      return;
    }

    state.lang = language;
    state.phase = "pre";
    state.baseline = null;

    $("question-input").value = "";
    $("assessment-response").value = "";

    $("answer-card").hidden = true;
    $("assessment-result").hidden = true;
    $("comparison-card").hidden = true;
    $("repeat-button").hidden = true;

    $("faq-list").replaceChildren();
    $("lesson-select").replaceChildren();

    notice("");
    translate();
    loadCatalog();
  }

  function start() {
    document.querySelectorAll(".lang-button")
      .forEach((button) => {
        button.addEventListener("click", () => {
          changeLanguage(button.dataset.lang);
        });
      });

    document.querySelectorAll(".tab-button")
      .forEach((button) => {
        button.addEventListener("click", () => {
          showTab(button.dataset.tab);
        });
      });

    $("question-form").addEventListener(
      "submit",
      (event) => {
        event.preventDefault();
        askQuestion();
      }
    );

    $("assessment-form").addEventListener(
      "submit",
      (event) => {
        event.preventDefault();
        assessResponse();
      }
    );

    $("lesson-select").addEventListener(
      "change",
      displayLesson
    );

    $("repeat-button").addEventListener(
      "click",
      () => {
        $("assessment-response").value = "";
        $("assessment-response").focus();
      }
    );

    translate();
    showTab("ask");
    loadCatalog();
  }

  if (document.readyState === "loading") {
    document.addEventListener(
      "DOMContentLoaded",
      start,
      { once: true }
    );
  } else {
    start();
  }
})();
