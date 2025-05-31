$("#run").on("click", () => tryCatch(run));

async function run() {
  await Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getActiveWorksheet();
    const salesRange = sheet.getRange("G2:G19");
    salesRange.load("values");

    await context.sync();

    const salesValues = salesRange.values;
    const formatRange = [];

    for (let i = 0; i < salesValues.length; i++) {
      if (salesValues[i][0] > 600) {
        formatRange.push(`G${i + 2}`); // Adjust for header row
      }
    }

    if (formatRange.length > 0) {
      const highlightRange = sheet.getRange(formatRange.join(","));
      highlightRange.format.fill.color = "red";
      highlightRange.format.font.color = "white";
    }

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