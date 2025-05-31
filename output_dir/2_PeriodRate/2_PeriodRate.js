$("#run").on("click", () => tryCatch(run));

async function run() {
  await Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getActiveWorksheet();
    const range = sheet.getUsedRange();
    range.load("values");

    await context.sync();

    const adjustedRates = range.values.map((row, index) => {
      if (index === 0) return ["Adjusted Annual Rate"]; // Header row
      return [row[0] + 1.0]; // Add 1.0 to Annual Rate
    });

    const adjustedRateRange = sheet.getRange(`C1:C${adjustedRates.length}`);
    adjustedRateRange.values = adjustedRates;

    await context.sync();
  });
}

/** Default helper for invoking an action and handling errors. */
async function tryCatch(callback) {
  try {
    await callback();
  } catch (error) {
    // Note: In a production add-in, you'd want to notify the user through your add-in's UI.
    console.error(error);
  }
}