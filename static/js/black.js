const { createApp, ref } = Vue;

createApp({
  setup() {
    // Mock data from the database
    const banReason = ref("Frequent cancellation");
    const banDuration = ref("3 Days (Until 2024-02-15)");

    // Fun messages pool
    const funnyMessages = [
      "Your account needs a little break.",
      "Our system elves are cleaning up your mess.",
      "This operation confused the server.",
      "Detected your unique talent. Enjoy this timeout!",
      "Your actions were too awesome. Triggered safety mode.",
    ];

    // Get a random fun message
    const getRandomMessage = () => {
      return funnyMessages[Math.floor(Math.random() * funnyMessages.length)];
    };

    // Initialize randomMessage with a random message
    const randomMessage = ref(getRandomMessage());

    // Play sound effect
    const soundEffect = ref(null);
    const playSound = () => {
      if (soundEffect.value) {
        soundEffect.value.play();
      }
    };

    return {
      banReason,
      banDuration,
      randomMessage, // 暴露 randomMessage 到模板
      playSound,
      soundEffect,
    };
  },
}).mount("#app");