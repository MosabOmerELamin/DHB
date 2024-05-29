// $.ajax({
//     url: "/slides/channel/join",
//     method: "POST",
//     contentType: "application/json",
//     data: JSON.stringify({
//         jsonrpc: "2.0",
//         method: "call",
//         params: {
//             channel_id: "yourChannelIdValue", // Adjust as needed
//         },
//         id: Math.floor(Math.random() * 1000)
//     }),
//     success: function (response) {
//         if (response.success && response.redirect_url) {
//             window.location.href = response.redirect_url;
//         }
//     },
//     error: function (error) {
//         console.error("Error joining the course:", error);
//     }
// });